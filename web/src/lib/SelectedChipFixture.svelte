<script lang="ts">
	interface Props {
		token: string;
		onRemove: (token: string) => void;
	}
	let { token, onRemove }: Props = $props();
</script>

<!-- Mirrors the selected-chip badge markup from +page.svelte -->
<span
	class="selected-chip"
	role="button"
	tabindex="0"
	onclick={() => onRemove(token)}
	onkeydown={(e) => {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			onRemove(token);
		}
	}}
>
	{token} ×
</span>
