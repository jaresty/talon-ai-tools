import { base } from '$app/paths';
import { json } from '@sveltejs/kit';

export const prerender = true;

export function GET() {
	return json({
		name: 'bar prompt builder',
		short_name: 'bar',
		start_url: `${base}/`,
		scope: `${base}/`,
		display: 'standalone',
		background_color: '#1a1a1a',
		theme_color: '#1a1a1a',
		icons: [
			{ src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
			{ src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
			{
				src: '/icon-512.png',
				sizes: '512x512',
				type: 'image/png',
				purpose: 'maskable'
			}
		]
	});
}
