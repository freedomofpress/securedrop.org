const fpfWebpackConfig = require("fpf-wagtail-common/config/webpack.js");

module.exports = fpfWebpackConfig({
	rootDir: __dirname,
	entry: {
		common: "./client/common/js/common.js",
		tor: "./client/tor/js/torEntry.js",
	},
});
