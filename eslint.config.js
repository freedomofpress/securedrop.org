const { defineConfig, globalIgnores } = require("eslint/config");
const js = require("@eslint/js");
const importPlugin = require("eslint-plugin-import");
const globals = require("globals");

module.exports = defineConfig([
	globalIgnores([
		"debug/static/debug/jquery.js",
		"coverage/",
		"htmlcov/",
		"build/",
		".venv/",
	]),

	{
		files: ["client/**/*.js"],
		extends: [js.configs.recommended, importPlugin.flatConfigs.recommended],
		languageOptions: {
			// eslint-plugin-import's recommended config sets ecmaVersion: 2018,
			// which can't parse newer syntax such as optional catch binding.
			ecmaVersion: "latest",
			globals: globals.browser,
		},
	},

	{
		// Scripts served directly by Django's static files, not bundled by webpack.
		files: ["securedrop/static/js/*.js"],
		extends: [js.configs.recommended],
		languageOptions: {
			sourceType: "script",
			globals: globals.browser,
		},
	},

	{
		// Build tool configs at the repo root, which run in Node.
		files: ["*.config.{js,mjs}"],
		extends: [js.configs.recommended],
		languageOptions: {
			globals: globals.node,
		},
	},

	{
		files: ["*.config.js"],
		languageOptions: {
			sourceType: "commonjs",
		},
	},
]);
