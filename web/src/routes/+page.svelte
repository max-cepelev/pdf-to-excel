<script lang="ts">
	import {
		Checkbox,
		FileUploader,
		Label,
		notification,
		Typography,
		type FileUploaderUploadOptions,
		type UploadFile
	} from '@max-ts/svelte';
	import { onMount } from 'svelte';
	import { convertPdf, fetchConfig, plural, type ServiceConfig } from '#lib/convert.ts';

	const MAX_FILES = 20;

	let files = $state<UploadFile[]>([]);
	let singleSheet = $state(false);
	let config = $state<ServiceConfig>({ maxFileMb: 50, maxPages: 500 });

	onMount(async () => {
		config = await fetchConfig().catch(() => config);
	});

	async function upload(
		fileId: string,
		pdf: File,
		{ signal, setProgress }: FileUploaderUploadOptions
	) {
		// без total компонент показывает плавный «примерный» прогресс — основное время уходит на конвертацию
		setProgress(fileId, { loaded: 0 });

		const { xlsx, stats } = await convertPdf(pdf, { singleSheet, signal });
		const summary = [
			plural(stats.tables, ['таблица', 'таблицы', 'таблиц']),
			plural(stats.rows, ['строка', 'строки', 'строк']),
			plural(stats.pages, ['страница', 'страницы', 'страниц'])
		].join(' · ');

		if (stats.mode === 'plain') {
			notification.warning(`${xlsx.name}: таблиц не найдено`, {
				content: 'Текст выгружен построчно на лист «Текст»'
			});
		} else if (stats.mode === 'text') {
			notification.info(`${xlsx.name} готов`, {
				content: `${summary}. Таблицы без рамок распознаны по выравниванию текста — проверьте результат`
			});
		} else {
			notification.success(`${xlsx.name} готов`, { content: summary });
		}

		return { id: fileId, name: xlsx.name, type: xlsx.type, size: xlsx.size, file: xlsx };
	}
</script>

<main>
	<header>
		<Typography variant="h3" component="h1">PDF → Excel</Typography>
		<Typography variant="body2" color="secondary">
			Находит таблицы в PDF и сохраняет их в .xlsx: каждая таблица — на своём листе, числа и даты —
			настоящими числами и датами. Таблицы, разорванные между страницами, склеиваются.
		</Typography>
	</header>

	<FileUploader
		bind:value={files}
		isMultiple
		maxFileCount={MAX_FILES}
		accept={['.pdf']}
		maxFileSize={config.maxFileMb * 1024 * 1024}
		placeholder="Перетащите PDF сюда или выберите на устройстве"
		onUploadFile={upload}
		getErrorMessage={(_, error) => error.message}
	/>

	<div class="option">
		<Checkbox id="single-sheet" bind:checked={singleSheet} />
		<Label for="single-sheet">Все таблицы на одном листе</Label>
	</div>

	<Typography variant="caption" color="muted" component="p">
		Файлы обрабатываются в памяти и не сохраняются на сервере. Сканы без текстового слоя не
		поддерживаются. До {plural(config.maxPages, ['страницы', 'страниц', 'страниц'])} в файле.
	</Typography>
</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-5);
		max-width: 680px;
		margin: 0 auto;
		padding: var(--spacing-16) var(--spacing-4);
	}

	header {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-2);
	}

	.option {
		display: flex;
		align-items: center;
		gap: var(--spacing-2);
	}
</style>
