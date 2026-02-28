import type { Grammar, CrossAxisPair } from './grammar.js';

export interface Conflict {
	tokenA: string;
	axisA: string;
	tokenB: string;
	axisB: string;
}

/**
 * Find all pairwise conflicts in the current selection using
 * hierarchy.axis_incompatibilities from the grammar JSON.
 *
 * The structure is: { axis: { token: [incompatible_token, ...] } }
 * Conflicts are symmetric — we surface each pair once.
 */
export function findConflicts(
	grammar: Grammar,
	selected: Record<string, string[]>
): Conflict[] {
	const incompatMap = grammar.hierarchy.axis_incompatibilities ?? {};
	const conflicts: Conflict[] = [];
	const seen = new Set<string>();

	for (const [axisA, tokensA] of Object.entries(selected)) {
		for (const tokenA of tokensA) {
			const rules = incompatMap[axisA]?.[tokenA] ?? [];
			for (const bad of rules) {
				// bad may be "axis:token" or just "token" — normalise
				let axisB = '';
				let tokenB = bad;
				if (bad.includes(':')) {
					[axisB, tokenB] = bad.split(':', 2);
				} else {
					// find which axis contains this token
					axisB =
						Object.entries(selected).find(([, toks]) => toks.includes(bad))?.[0] ?? '';
				}
				if (!axisB) continue;
				if (!(selected[axisB] ?? []).includes(tokenB)) continue;

				const key = [tokenA, tokenB].sort().join('|');
				if (seen.has(key)) continue;
				seen.add(key);
				conflicts.push({ tokenA, axisA, tokenB, axisB });
			}
		}
	}
	// Also surface cautionary pairs from cross_axis_composition.
	const cac = grammar.axes.cross_axis_composition;
	if (cac) {
		for (const [axisA, byToken] of Object.entries(cac)) {
			for (const [tokenA, byAxis] of Object.entries(byToken)) {
				if (!(selected[axisA] ?? []).includes(tokenA)) continue;
				for (const [axisB, pair] of Object.entries(byAxis as Record<string, CrossAxisPair>)) {
					for (const tokenB of Object.keys(pair.cautionary ?? {})) {
						if (!(selected[axisB] ?? []).includes(tokenB)) continue;
						const key = [tokenA, tokenB].sort().join('|');
						if (seen.has(key)) continue;
						seen.add(key);
						conflicts.push({ tokenA, axisA, tokenB, axisB });
					}
				}
			}
		}
	}

	return conflicts;
}
