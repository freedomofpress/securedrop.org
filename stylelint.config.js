module.exports = {
	extends: 'stylelint-config-standard-scss',
	customSyntax: 'postcss-scss',
	rules: {
		'rule-empty-line-before': null,
		'declaration-empty-line-before': null,
		'at-rule-empty-line-before': null,
		'comment-empty-line-before': null,
		'no-descending-specificity': null,

		// This codebase uses BEM-style (__, --) class/mixin/variable names,
		// which don't fit a plain kebab-case pattern.
		'selector-class-pattern': null,
		'scss/at-mixin-pattern': null,
		'scss/dollar-variable-pattern': null,

		// Would require migrating every call site to the "sass:*" module
		// functions (map.get, color.adjust, etc.) - out of scope here.
		'scss/no-global-function-names': null,

		// Stylistic modernizations that would touch most files without
		// fixing a real bug.
		'color-hex-length': null,
		'value-keyword-case': null,
		'color-function-notation': null,
		'color-function-alias-notation': null,
		'alpha-value-notation': null,
		'media-feature-range-notation': null,
		'declaration-block-no-redundant-longhand-properties': null,
		'scss/comment-no-empty': null,
		'scss/dollar-variable-empty-line-before': null,
		'scss/double-slash-comment-empty-line-before': null,
	},
}
