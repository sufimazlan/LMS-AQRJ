<script lang="ts">
	// Placeholder mark until AQRJ supplies its own logo. Keep in step with static/icons/icon.svg.
	let { size = 32 }: { size?: number } = $props();
</script>

<svg
	width={size}
	height={size}
	viewBox="0 0 64 64"
	xmlns="http://www.w3.org/2000/svg"
	aria-hidden="true"
	class="shrink-0"
>
	<rect width="64" height="64" rx="14" fill="#1f5539" />
	<path
		d="M32 24c-5-4-12-5-18-4v24c6-1 13 0 18 4 5-4 12-5 18-4V20c-6-1-13 0-18 4z"
		fill="#fbf8f1"
	/>
	<path d="M32 24v24" stroke="#1f5539" stroke-width="2" />
	<circle cx="32" cy="13" r="3" fill="#d4a942" />
</svg>
