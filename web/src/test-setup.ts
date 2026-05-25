// jsdom doesn't implement Worker — provide a minimal stub
if (typeof globalThis.Worker === 'undefined') {
	globalThis.Worker = class {
		postMessage() {}
		terminate() {}
		onmessage: ((e: MessageEvent) => void) | null = null;
		addEventListener() {}
		removeEventListener() {}
		dispatchEvent() { return false; }
	} as unknown as typeof Worker;
}

// jsdom doesn't implement ResizeObserver — provide a minimal stub
if (typeof globalThis.ResizeObserver === 'undefined') {
	globalThis.ResizeObserver = class {
		observe() {}
		unobserve() {}
		disconnect() {}
	};
}

// jsdom doesn't implement window.matchMedia — provide a minimal stub
Object.defineProperty(window, 'matchMedia', {
	writable: true,
	value: (query: string) => ({
		matches: false,
		media: query,
		onchange: null,
		addListener: () => {},
		removeListener: () => {},
		addEventListener: () => {},
		removeEventListener: () => {},
		dispatchEvent: () => false
	})
});
