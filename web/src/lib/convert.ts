export type ConversionStats = {
	pages: number;
	tables: number;
	rows: number;
	/** lines — таблицы с рамками, text — по выравниванию текста, plain — таблиц нет, выгружен текст */
	mode: 'lines' | 'text' | 'plain';
};

export type ServiceConfig = { maxFileMb: number; maxPages: number };

const XLSX_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

export async function fetchConfig(): Promise<ServiceConfig> {
	const response = await fetch('/api/config');
	return response.json();
}

export async function convertPdf(
	pdf: File,
	{ singleSheet, signal }: { singleSheet: boolean; signal: AbortSignal }
): Promise<{ xlsx: File; stats: ConversionStats }> {
	const body = new FormData();
	body.append('file', pdf);

	const response = await fetch(`/api/convert?single_sheet=${singleSheet}`, {
		method: 'POST',
		body,
		signal
	});

	if (!response.ok) {
		const error = await response.json().catch(() => null);
		throw new Error(error?.detail ?? `Ошибка сервера (${response.status})`);
	}

	const name = pdf.name.replace(/\.pdf$/i, '') + '.xlsx';
	return {
		xlsx: new File([await response.blob()], name, { type: XLSX_TYPE }),
		stats: JSON.parse(response.headers.get('X-Conversion-Stats') ?? '{}')
	};
}

export function plural(n: number, [one, few, many]: [string, string, string]) {
	const mod10 = n % 10;
	const mod100 = n % 100;
	const word =
		mod10 === 1 && mod100 !== 11
			? one
			: mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)
				? few
				: many;
	return `${n.toLocaleString('ru-RU')} ${word}`;
}
