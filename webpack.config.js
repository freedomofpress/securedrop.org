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
				loader: "babel-loader",
				include: path.resolve(__dirname, "client"),
			},
			{
				test: /\.scss$/,
				type: "css",
				loader: "sass-loader",
				options: {
					sassOptions: {
						loadPaths: [
							path.resolve(__dirname, "node_modules"),
							path.resolve(__dirname, "common/static/fonts"),
							path.resolve(__dirname, "client/common/scss"),
						],
					},
				},
			},
		],
	},

	plugins: [new BundleTracker({ path: __dirname })],
};
