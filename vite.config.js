const path = require('path')
const { defineConfig } = require('vite')

// Must match Django's real STATIC_URL. The common app's static/ files are
// served directly under STATIC_URL with no per-app prefix
// (AppDirectoriesFinder), so this is "/static/", not "/common/static/".
const STATIC_URL = process.env.STATIC_URL || '/static/'

module.exports = defineConfig({
	// Vite resolves any CSS url() starting with "/" (e.g. the
	// $static-url-prefixed font/image references below) against publicDir.
	// Pointing publicDir at the common app (the app whose static/
	// directory those files actually live in), rather than letting Vite's
	// own asset pipeline own them, makes Vite recognize them as
	// already-published files at their real served URL and leave them
	// alone, instead of re-emitting duplicate hashed copies into
	// build/static/bundles/. copyPublicDir is off so Vite doesn't also
	// bulk-copy the rest of the common app (models, templates, etc.) into
	// the build output.
	publicDir: path.resolve(__dirname, 'common'),
	build: {
		outDir: path.resolve(__dirname, 'build/static/bundles'),
		emptyOutDir: true,
		copyPublicDir: false,
		// Vite defaults to baseline-widely-available, but making it explicit.
		target: 'baseline-widely-available',
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
