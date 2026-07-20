const js = require('@eslint/js')
const globals = require('globals')
const stylistic = require('@stylistic/eslint-plugin')

module.exports = [
	{
		ignores: ['build/**', 'node_modules/**'],
	},
	{
		...js.configs.recommended,
		files: ['client/**/*.js'],
		plugins: {
			'@stylistic': stylistic,
		},
		languageOptions: {
			ecmaVersion: 'latest',
			sourceType: 'module',
			globals: {
				...globals.browser,
			},
		},
		rules: {
			...js.configs.recommended.rules,
			'@stylistic/indent': ['error', 'tab'],
		},
	},
]
