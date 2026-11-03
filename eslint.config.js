const { defineConfig } = require("eslint/config");
const js = require("@eslint/js");
const fpfEslintConfig = require("fpf-wagtail-common/config/eslint.js");
const globals = require("globals");

module.exports = defineConfig([
	...fpfEslintConfig({
		files: ["client/**/*.js"],
		ignores: ["debug/static/debug/jquery.js"],
	}),

	{
		// Scripts served directly by Django's static files, not bundled by webpack.
		files: ["securedrop/static/js/*.js"],
		extends: [js.configs.recommended],
		languageOptions: {
			sourceType: "script",
			globals: globals.browser,
		},
	},
]);
