# PDF → Excel

Веб-сервис: загружаете PDF — получаете .xlsx с таблицами.

- каждая найденная таблица — на своём листе (или все на одном — галочка в интерфейсе);
- таблица, разорванная между страницами, склеивается, повторы шапки убираются;
- числа (`1 234,56`) и даты (`14.09.2026`) записываются как числа и даты; артикулы с ведущим нулём
  и длинные номера (ИНН, счета) остаются текстом;
- если таблиц с рамками нет — ищутся таблицы по выравниванию текста; если нет и их — текст выгружается построчно;
- сканы без текстового слоя и PDF с паролем не поддерживаются (сервис сообщает об этом).

Файлы обрабатываются в памяти и нигде не сохраняются.

## Устройство

```
app/converter.py   извлечение таблиц (PyMuPDF) и запись .xlsx (openpyxl)
app/main.py        FastAPI: POST /api/convert, GET /api/config, GET /api/health + раздача фронтенда
web/               SvelteKit (adapter-static) + @max-ts/svelte (FileUploader)
Dockerfile         node собирает web/ в статику → python:3.13-slim, один процесс uvicorn на :8000
```

## Деплой в Dokploy

Образ собирается локально под `linux/amd64` и загружается в registry:

```bash
cp .env.deploy.example .env.deploy   # указать REGISTRY (и при желании DOKPLOY_WEBHOOK)
docker login <registry>
make push
```

Образ получает два тега: `<дата-время>` и `latest`. В Dokploy: приложение с источником Docker →
образ `<REGISTRY>/pdf-to-excel:latest`, порт контейнера `8000`, health check `/api/health`.

Сервис публичный, поэтому лучше включить Basic Auth в настройках приложения в Dokploy.

Переменные окружения (необязательно):

| Переменная       | По умолчанию | Что делает                           |
|------------------|--------------|--------------------------------------|
| `MAX_FILE_MB`    | 50           | максимальный размер PDF              |
| `MAX_PAGES`      | 500          | максимальное число страниц           |
| `MAX_CONCURRENT` | 2            | сколько файлов конвертируются разом  |

Если перед сервисом стоит свой лимит на размер запроса (Traefik/Nginx), он должен быть не меньше `MAX_FILE_MB`.

## Локальная разработка

Запуск готового образа: `make run` → http://localhost:8000

С горячей перезагрузкой — в двух терминалах:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

```bash
cd web && pnpm install && pnpm dev   # http://localhost:5173, /api проксируется на :8000
```

Без веб-интерфейса, из командной строки:

```bash
.venv/bin/python -m app.converter file.pdf other.pdf -o excel/ [--single-sheet]
```

PyMuPDF распространяется по лицензии AGPL-3.0.
