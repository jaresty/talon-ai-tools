// ADR-0231: SPA Prompt History
export const HISTORY_KEY = 'bar-history';
export const HISTORY_MAX = 50;

export type HistoryTrigger =
	| 'copy-command'
	| 'copy-prompt'
	| 'share-prompt'
	| 'share-link'
	| 'copy-link'
	| 'open-link';

export interface HistoryEntry {
	ts: string; // ISO 8601 + monotonic suffix for uniqueness
	hash: string;
	trigger: HistoryTrigger;
	subject_preview: string;
	command_preview: string;
}

let _seq = 0;
function uniqueTs(): string {
	return `${new Date().toISOString()}-${_seq++}`;
}

export function loadHistory(storage: Storage): HistoryEntry[] {
	try {
		const raw = storage.getItem(HISTORY_KEY);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? (parsed as HistoryEntry[]) : [];
	} catch {
		return [];
	}
}

function saveHistory(storage: Storage, entries: HistoryEntry[]): void {
	storage.setItem(HISTORY_KEY, JSON.stringify(entries));
}

export function addHistoryEntry(
	storage: Storage,
	entry: Omit<HistoryEntry, 'ts'>
): void {
	const entries = loadHistory(storage);
	// Dedup: skip if last entry has same hash (same state, e.g. double-click or open-link
	// followed immediately by copy-link on the same state)
	if (entries.length > 0 && entries[0].hash === entry.hash) return;
	const newEntry: HistoryEntry = { ts: uniqueTs(), ...entry };
	const updated = [newEntry, ...entries].slice(0, HISTORY_MAX);
	saveHistory(storage, updated);
}

export function deleteHistoryEntry(storage: Storage, ts: string): void {
	const entries = loadHistory(storage);
	saveHistory(storage, entries.filter(e => e.ts !== ts));
}

export function clearHistory(storage: Storage): void {
	storage.removeItem(HISTORY_KEY);
}
