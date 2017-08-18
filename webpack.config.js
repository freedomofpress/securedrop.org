var webpack       = require('webpack');
var merge         = require('webpack-merge');
var autoprefixer  = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var path = require('path');

var TARGET = process.env.npm_lifecycle_event;
process.env.BABEL_ENV = TARGET;

var target = __dirname + '/build/static/bundles';

var STATIC_URL = process.env.STATIC_URL || '/static/';
var sassData = '$static-url: "' + STATIC_URL + '";';
console.log('Using STATIC_URL', STATIC_URL);


var common = {
	entry: {
		common: __dirname + '/client/common/js/common.js',
	},

	output: {
		path: target,
		filename: '[name].js'
	},

	resolve: {
		alias: {
			'~': __dirname + '/client/common/js',
			modernizr$: path.resolve(__dirname, '.modernizrrc')
		},
		extensions: ['.js', '.jsx'],
		modules: ['node_modules']
	},

	module: {
		rules: [
			{
				test: /\.jsx?$/,
				use: [
					{
						loader: 'babel-loader',
						query: {
							presets: ['react', 'es2015', 'stage-0', 'stage-1', 'stage-2'],
							plugins: ['add-module-exports']
						},
					}
				],
				include: [
					path.join(__dirname, '/client/common/js'),
				],
			},
			{
				test: /\.s[ca]ss$/,
				use: ExtractTextPlugin.extract({
					fallback: 'style-loader',
					use: [
						'css-loader',
						'postcss-loader',
						{
							loader: 'sass-loader',
							options: {
								includePaths: [path.resolve(__dirname, 'node_modules/')],
								data: sassData
							}
						}
					]
				}),
			},
			{
				test: /\.css$/,
				use: ExtractTextPlugin.extract({
					fallback: 'style-loader',
					use: [
						'css-loader',
						'postcss-loader'
					]
				})
			},
			// Currently unused, but we'll want it if we install modernizr:
			{
				test: /\.modernizrrc$/,
				use: ['modernizr']
			}
		]
	},

	plugins: [
		new ExtractTextPlugin({
			filename: (getPath) => {
				if (TARGET === 'build') {
					return getPath('[name]-[hash].css');
				} else {
					return getPath('[name].css');
				}
			}
		}),

		new BundleTracker({
			path: target,
			filename: './webpack-stats.json'
		})
	]
};

if (TARGET === 'build') {
	module.exports = merge(common, {
		output: {
			filename: '[name]-[hash].js'
		},
		plugins: [
			new webpack.DefinePlugin({
				'process.env': { 'NODE_ENV': JSON.stringify('production') }
			})
		]
	});
}

if (TARGET === 'start') {
	module.exports = merge(common, {
		devtool: 'eval-source-map',
		devServer: {
			contentBase: target,
			progress: true,
		}
	});
}
