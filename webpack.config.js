var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var MiniCssExtractPlugin = require("mini-css-extract-plugin");
var path = require("path");

var TARGET = process.env.npm_lifecycle_event;
process.env.BABEL_ENV = TARGET;

var target = __dirname + "/build/static/bundles";

var STATIC_URL = process.env.STATIC_URL || "/common/static/";
var scssData = '@use "base/config" with ($static-url: "' + STATIC_URL + '");';
console.log("Using STATIC_URL", STATIC_URL);

var common = {
	entry: {
		common: __dirname + "/client/common/js/common.js",
		tor: __dirname + "/client/tor/js/torEntry.js",
	},

	output: {
		path: target,
		filename: "[name].js",
	},

	resolve: {
		extensions: [".js"],
		modules: ["node_modules"],
	},

	module: {
		rules: [
			{
				test: /\.js$/,
				use: [
					{
						loader: "babel-loader",
						options: {
							presets: ["@babel/preset-env"],
						},
					},
				],
				include: [
					path.join(__dirname, "/client/common/js"),
					path.join(__dirname, "/client/tor/js"),
				],
			},
			{
				test: /\.scss$/,
				use: [
					MiniCssExtractPlugin.loader,
					"css-loader",
					{
						loader: "sass-loader",
						options: {
							sassOptions: {
								loadPaths: [
									path.resolve(__dirname, "node_modules/"),
									path.resolve(__dirname, "common/static/fonts/"),
									path.resolve(__dirname, "client/common/scss/"),
								],
							},
							additionalData: scssData,
						},
					},
				],
			},
			{
				test: /\.css$/,
				use: [MiniCssExtractPlugin.loader, "css-loader"],
			},
			{
				test: /\.(png|svg|jpg|gif)$/,
				type: "asset/resource",
			},
			{
				test: /\.(woff|woff2|eot|ttf|otf)$/,
				type: "asset/resource",
			},
		],
	},

	plugins: [
		new MiniCssExtractPlugin({
			filename: TARGET === "build" ? "[name]-[contenthash].css" : "[name].css",
			chunkFilename: TARGET === "build" ? "[id]-[contenthash].css" : "[id].css",
		}),
		new BundleTracker({
			path: target,
			filename: "webpack-stats.json",
		}),
	],
};

if (TARGET === "build") {
	module.exports = {
		...common,
		output: {
			...common.output,
			filename: "[name]-[contenthash].js",
		},
		plugins: [
			...common.plugins,
			new webpack.DefinePlugin({
				"process.env": { NODE_ENV: JSON.stringify("production") },
			}),
		],
	};
}

if (TARGET === "start") {
	module.exports = {
		...common,
		output: { ...common.output, pathinfo: true },
	};
}
