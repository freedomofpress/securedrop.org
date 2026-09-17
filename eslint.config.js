const js = require("@eslint/js");
const importPlugin = require("eslint-plugin-import");
const prettier = require("eslint-config-prettier");
const globals = require("globals");

const jsFiles = ["client/**/*.js"];

module.exports = [
	{
		ignores: ["coverage/**", "build/**"],
	},

	{ files: jsFiles, ...js.configs.recommended },
	{ files: jsFiles, ...importPlugin.flatConfigs.recommended },
	{ files: jsFiles, ...prettier },

	{
		files: jsFiles,

		languageOptions: {
			// eslint-plugin-import's recommended config hardcodes ecmaVersion: 2018,
			// which is older than this codebase's syntax (e.g. optional chaining).
			// Override it back to the ESLint default so parsing doesn't regress.
			ecmaVersion: "latest",
			globals: {
				...globals.browser,
				// webpack injects a `module` binding into each bundled chunk for
				// its Hot Module Replacement API (module.hot).
				module: "readonly",
				// Matomo/Piwik's tracking snippet defines this on `window` before
				// our bundles run.
				_paq: "readonly",
			},
		},

		settings: {
			react: {
				version: "detect",
			},
			"import/resolver": {
				webpack: {
					config: {
						extensions: [".js"],
					},
				},
			},
		},

		rules: {
			// Allow a leading underscore to mark a parameter as intentionally
			// unused, e.g. one kept only for signature consistency with sibling
			// callback functions.
			"no-unused-vars": ["error", { argsIgnorePattern: "^_" }],

			// webpack.config.js only populates module.exports when run via the
			// `build`/`start` npm scripts (it branches on npm_lifecycle_event),
			// so requiring it here (e.g. from eslint-import-resolver-webpack)
			// yields an empty config and can't actually resolve aliases or
			// extension-less imports. Leave path resolution unchecked until
			// that export is restructured.
			"import/no-unresolved": "off",
		},
	},

	{
		files: ["**/*.test.js"],
		languageOptions: {
			globals: {
				...globals.jest,
			},
		},
	},
];
