const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");

const target = __dirname + "/build/static/bundles";

const STATIC_URL = process.env.STATIC_URL || "/common/static/";
const scssData = '@use "base/config" with ($static-url: "' + STATIC_URL + '");';
console.log("Using STATIC_URL", STATIC_URL);

// Exported as a function so the config is defined whenever it's loaded, not
// only under `npm run build`/`start`. argv.mode comes from --mode in those
// scripts; webpack sets process.env.NODE_ENV from it, so no DefinePlugin.
module.exports = (env, argv) => {
	const isProd = argv.mode === "production";

	return {
		entry: {
			common: __dirname + "/client/common/js/common.js",
			tor: __dirname + "/client/tor/js/torEntry.js",
		},

		output: {
			path: target,
			filename: isProd ? "[name]-[contenthash].js" : "[name].js",
			pathinfo: !isProd,
		},

		resolve: {
			extensions: [".js"],
		},

		module: {
			rules: [
				{
					test: /\.js$/,
					loader: "babel-loader",
					// webpack's --mode doesn't set NODE_ENV for the Node process, so
					// Babel would otherwise always use its 'development' env.
					options: { envName: isProd ? "production" : "development" },
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
