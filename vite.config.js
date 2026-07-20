const path = require('path')
const { defineConfig } = require('vite')

// Value used only to build the Sass $static-url variable below, which
// must match where the common app's static/ directory actually lives on
// disk relative to the project root (see publicDir/renderBuiltUrl below).
const STATIC_URL = process.env.STATIC_URL || '/common/static/'

module.exports = defineConfig({
	// Vite resolves any CSS url() starting with "/" (e.g. the
	// $static-url-prefixed font/image references below) against the
	// project root. Treating the whole project root as Vite's publicDir -
	// without letting Vite copy it wholesale into outDir - makes Vite
	// recognize those as already-published files and leave them alone,
	// instead of re-emitting duplicate hashed copies into
	// build/static/bundles/. renderBuiltUrl then rewrites the disk-relative
	// path Vite resolved them by into the URL Django actually serves them
	// at (STATIC_URL, with no "common" prefix, since AppDirectoriesFinder
	// serves an app's static/ directory contents directly under STATIC_URL).
	publicDir: path.resolve(__dirname),
	experimental: {
		renderBuiltUrl(filename, { type }) {
			if (type === 'public' && filename.startsWith('common/static/')) {
				return '/static/' + filename.slice('common/static/'.length)
			}
		},
	},
	build: {
		outDir: path.resolve(__dirname, 'build/static/bundles'),
		emptyOutDir: true,
		copyPublicDir: false,
		manifest: 'manifest.json',
		rollupOptions: {
			input: {
				common: path.resolve(__dirname, 'client/common/js/common.js'),
				tor: path.resolve(__dirname, 'client/tor/js/torEntry.js'),
			},
			output: {
				entryFileNames: 'assets/[name]-[hash].js',
				chunkFileNames: 'assets/[name]-[hash].js',
				assetFileNames: 'assets/[name]-[hash][extname]',
			},
		},
	},
	resolve: {
		alias: {
			'~': path.resolve(__dirname, 'client/common/js'),
			tor: path.resolve(__dirname, 'client/tor/js'),
		},
	},
	css: {
		preprocessorOptions: {
			scss: {
				api: 'modern',
				loadPaths: [
					path.resolve(__dirname, 'node_modules/'),
					path.resolve(__dirname, 'common/static/fonts/'),
				],
				additionalData: `$static-url: "${STATIC_URL}";\n`,
			},
		},
	},
})
