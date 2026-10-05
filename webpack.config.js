const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");

const target = __dirname + "/build/static/bundles";

const STATIC_URL = process.env.STATIC_URL || "/common/static/";
const scssData = '@use "base/config" with ($static-url: "' + STATIC_URL + '");';
console.log("Using STATIC_URL", STATIC_URL);

// Exported as a function so the config is defined whenever it's loaded.
module.exports = (env, argv) => {
	// The npm scripts pass --config-node-env, which sets NODE_ENV in the Node
	// process. Use an explicit --mode if given, else NODE_ENV, else webpack's
	// own default, and set `mode` below so this config and webpack agree.
	const mode =
		argv.mode ??
		(process.env.NODE_ENV === "development" ? "development" : "production");
	const isProd = mode === "production";

	// In the bundles themselves, webpack replaces process.env.NODE_ENV based on
	// `mode` (optimization.nodeEnv), so no DefinePlugin is needed.
	return {
		mode,

		entry: {
			common: __dirname + "/client/common/js/common.js",
			tor: __dirname + "/client/tor/js/torEntry.js",
		},

		output: {
			path: target,
			filename: isProd ? "[name]-[contenthash].js" : "[name].js",
			clean: true,
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
};
