const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");

const isProd = process.env.npm_lifecycle_event === "build";
const isDev = process.env.npm_lifecycle_event === "start";

const target = __dirname + "/build/static/bundles";

const STATIC_URL = process.env.STATIC_URL || "/common/static/";
const scssData = '@use "base/config" with ($static-url: "' + STATIC_URL + '");';
console.log("Using STATIC_URL", STATIC_URL);

const common = {
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
	},

	module: {
		rules: [
			{
				test: /\.js$/,
				loader: "babel-loader",
				include: [path.join(__dirname, "/client")],
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
			filename: isProd ? "[name]-[contenthash].css" : "[name].css",
			chunkFilename: isProd ? "[id]-[contenthash].css" : "[id].css",
		}),
		new BundleTracker({
			path: target,
			filename: "webpack-stats.json",
		}),
	],
};

if (isProd) {
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

if (isDev) {
	module.exports = {
		...common,
		output: { ...common.output, pathinfo: true },
	};
}
