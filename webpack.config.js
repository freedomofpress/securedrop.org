const BundleTracker = require("webpack-bundle-tracker");
const path = require("path");

module.exports = {
	context: __dirname,

	entry: {
		common: "./client/common/js/common.js",
		tor: "./client/tor/js/torEntry.js",
	},

	output: {
		path: path.resolve(__dirname, "build/static/bundles"),
		filename: "[name]-[contenthash].js",
		clean: true,
	},

	module: {
		rules: [
			{
				test: /\.js$/,
				// Babel gets its env from NODE_ENV, which is set by --config-node-env in
				// the npm scripts.
				loader: "babel-loader",
				include: path.resolve(__dirname, "client"),
			},
			{
				test: /\.scss$/,
				type: "css",
				loader: "sass-loader",
			},
		],
	},

	plugins: [new BundleTracker({ path: __dirname })],
};
