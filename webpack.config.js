const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
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
				use: [
					MiniCssExtractPlugin.loader,
					"css-loader",
					{
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
		new MiniCssExtractPlugin({ filename: "[name]-[contenthash].css" }),
		new BundleTracker({ path: __dirname }),
	],
};
