export const PRESETS_KEY = 'bar-presets';

export interface SpaPresetPersona {
	preset?: string;
	voice?: string;
	audience?: string;
	tone?: string;
	intent?: string;
}

// Matches CLI presetFile schema v3 (source: 'spa')
export interface SpaPreset {
	version: 3;
	name: string;
	saved_at: string; // ISO 8601
	source: 'spa';
	tokens: string[];
	result: {
		axes: Record<string, string[]>;
		persona: SpaPresetPersona;
	};
}

export function slugifyPresetName(name: string): string {
	const trimmed = name.trim().toLowerCase();
	if (!trimmed) return 'preset';
	const slug = trimmed.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
	return slug || 'preset';
}

function loadStore(storage: Storage): Record<string, SpaPreset> {
	try {
		const raw = storage.getItem(PRESETS_KEY);
		if (!raw) return {};
		const parsed = JSON.parse(raw);
		if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
			return parsed as Record<string, SpaPreset>;
		}
		return {};
	} catch {
		return {};
	}
}

function saveStore(storage: Storage, store: Record<string, SpaPreset>): void {
	storage.setItem(PRESETS_KEY, JSON.stringify(store));
}

export function savePreset(
	storage: Storage,
	name: string,
	tokens: string[],
	axes: Record<string, string[]>,
	persona: SpaPresetPersona
): void {
	const store = loadStore(storage);
	const slug = slugifyPresetName(name);
	store[slug] = {
		version: 3,
		name,
		saved_at: new Date().toISOString(),
		source: 'spa',
		tokens,
		result: { axes, persona }
	};
	saveStore(storage, store);
}

export function listPresets(storage: Storage): SpaPreset[] {
	const store = loadStore(storage);
	return Object.values(store).sort((a, b) => b.saved_at.localeCompare(a.saved_at));
}

export function deletePreset(storage: Storage, name: string): void {
	const store = loadStore(storage);
	const slug = slugifyPresetName(name);
	delete store[slug];
	saveStore(storage, store);
}
