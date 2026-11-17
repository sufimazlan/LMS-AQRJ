<script lang="ts">
	import { asset } from '$app/paths';

	// The AQRJ emblem. The picture is static/icons/logo.webp (192 px, clear background).
	let { size = 32 }: { size?: number } = $props();
</script>

<img
	src={asset('icons/logo.webp')}
	width={size}
	height={size}
	alt=""
	decoding="async"
	class="shrink-0"
/>
