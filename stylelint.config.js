module.exports = {
	extends: 'stylelint-config-standard',
	customSyntax: 'postcss-sass',
	rules: {
		'indentation': 'tab',
		'string-quotes': 'single',
		'rule-empty-line-before': null,
		'declaration-empty-line-before': null,
		'at-rule-empty-line-before': null,
		'comment-empty-line-before': null,
		'no-descending-specificity': null,
	},
}
