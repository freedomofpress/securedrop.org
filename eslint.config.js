const js = require('@eslint/js')
const globals = require('globals')
const prettier = require('eslint-config-prettier')

module.exports = [
	{
		ignores: ['build/**', 'node_modules/**'],
	},
	{
		...js.configs.recommended,
		files: ['client/**/*.js'],
		languageOptions: {
			ecmaVersion: 'latest',
			sourceType: 'module',
			globals: {
				...globals.browser,
			},
		},
		rules: {
			...js.configs.recommended.rules,
		},
	},
	prettier,
]
