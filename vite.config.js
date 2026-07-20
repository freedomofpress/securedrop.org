const path = require('path')
const { defineConfig } = require('vite')

const STATIC_URL = process.env.STATIC_URL || '/common/static/'

module.exports = defineConfig({
	// Must match Django's STATIC_URL + DJANGO_VITE's static_url_prefix: Vite
	// resolves any CSS url() starting with "/" (e.g. the $static-url-prefixed
	// font/image references below) against the project root and re-emits them
	// as hashed assets here, so this is where those URLs need to resolve.
	base: '/static/bundles/',
	build: {
		outDir: path.resolve(__dirname, 'build/static/bundles'),
		emptyOutDir: true,
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
