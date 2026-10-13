import asyncio
import json
import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from app.converter import ConversionError, convert

MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "50"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "500"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "2"))
QUEUE_TIMEOUT = 60
STATIC_DIR = Path(os.getenv("STATIC_DIR", "web/build"))

XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

log = logging.getLogger("uvicorn.error")
app = FastAPI(title="PDF → Excel", docs_url=None, redoc_url=None)
# конвертация грузит CPU, поэтому одновременно обрабатываем не больше MAX_CONCURRENT файлов
slots = asyncio.Semaphore(MAX_CONCURRENT)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config")
def config():
    return {"maxFileMb": MAX_FILE_MB, "maxPages": MAX_PAGES}


@app.post("/api/convert")
async def convert_pdf(file: UploadFile, single_sheet: bool = Query(False)):
    limit = MAX_FILE_MB * 1024 * 1024
    if file.size is not None and file.size > limit:
        raise HTTPException(413, f"Файл больше {MAX_FILE_MB} МБ")
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"Файл больше {MAX_FILE_MB} МБ")
    if not data.startswith(b"%PDF"):
        raise HTTPException(415, "Это не PDF")

    try:
        await asyncio.wait_for(slots.acquire(), QUEUE_TIMEOUT)
    except TimeoutError:
        raise HTTPException(503, "Сервис занят, попробуйте через минуту") from None
    started = time.perf_counter()
    try:
        result = await run_in_threadpool(convert, data, single_sheet=single_sheet, max_pages=MAX_PAGES)
    except ConversionError as exc:
        raise HTTPException(422, str(exc)) from None
    finally:
        slots.release()

    stats = {"pages": result.pages, "tables": result.tables, "rows": result.rows, "mode": result.mode}
    log.info("converted %d KB in %.1fs: %s", len(data) // 1024, time.perf_counter() - started, stats)
    return Response(result.xlsx, media_type=XLSX_TYPE, headers={"X-Conversion-Stats": json.dumps(stats)})


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="web")
