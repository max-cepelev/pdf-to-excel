<script lang="ts">
	import '@max-ts/svelte/reset.css';
	import '@max-ts/svelte/theme.css';
	import { NotificationContainer } from '@max-ts/svelte';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<title>PDF → Excel</title>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
<NotificationContainer />

<style>
	:global(body) {
		min-height: 100dvh;
		background: var(--colors-background-sidebar);
		color: var(--colors-text-primary);
	}
</style>
