const js = require("@eslint/js");
const importPlugin = require("eslint-plugin-import");
const prettier = require("eslint-config-prettier");
const globals = require("globals");

const jsFiles = ["client/**/*.js"];

module.exports = [
	{
		ignores: [
			"debug/static/debug/jquery.js",
			"coverage/**",
			"build/**",
			".venv/**",
		],
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
			globals: globals.browser,
		},
	},
];
