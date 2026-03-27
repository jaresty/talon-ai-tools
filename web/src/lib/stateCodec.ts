/**
 * Pure encode/decode for prompt state URL sharing.
 * Uses encodeURIComponent to handle non-Latin1 (Unicode) characters
 * before Base64 encoding, avoiding btoa InvalidCharacterError.
 */

export function encodeState(state: object): string {
	return btoa(encodeURIComponent(JSON.stringify(state)));
}

export function decodeState(raw: string): object | null {
	try {
		return JSON.parse(decodeURIComponent(atob(raw)));
	} catch {
		return null;
	}
}
