module.exports = {
	"extends": "airbnb",

	"plugins": [
		"react"
	],

	"settings": {
		"import/resolver": "webpack"
	},

	"parserOptions": {
		"ecmaFeatures": {
			"experimentalObjectRestSpread": true
		}
	},

	"rules": {
		"arrow-body-style": 0,
		"indent": ["error", "tab"],
		"no-underscore-dangle": 0,
		"react/jsx-indent": ["error", "tab"],
		"react/jsx-indent-props": ["error", "tab"],
		"react/jsx-no-bind": ["warn"],
		"import/no-unresolved": 0,
		"radix": ["error", "as-needed"],
		"react/no-deprecated": ["error", { "react": "0.15.2"  }],
		"semi": ["error", "never"]
	}
};
