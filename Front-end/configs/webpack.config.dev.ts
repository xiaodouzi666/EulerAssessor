import 'webpack-dev-server';
import path from 'path';
import fs from 'fs';
import webpack from 'webpack';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import { merge } from 'webpack-merge';
import { execSync, spawn } from 'child_process';
import ReactRefreshWebpackPlugin from '@pmmmwh/react-refresh-webpack-plugin';
import baseConfig from './webpack.config.base';
import webpackPaths from './webpack.paths';

const port = process.env.PORT || 8080;
// const manifest = path.resolve(webpackPaths.dllPath, 'renderer.json');

const configuration: webpack.Configuration = {
  devtool: 'inline-source-map',

  target: ['web'],

  output: {
    path: webpackPaths.distOuputPath,
    publicPath: '/',
    filename: 'renderer.dev.js',
  },
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx'],
    alias: {
      '@': path.resolve(__dirname, '../src'),
      // '@assets': path.resolve(__dirname, '../src/assets'),
      // '@components': path.resolve(__dirname, '../src/components'),
      // '@constants': path.resolve(__dirname, '../src/constants'),
      // '@utils': path.resolve(__dirname, '../src/utils'),
      // '@context': path.resolve(__dirname, '../src/context'),
      // '@lang': path.resolve(__dirname, '../src/lang'),
      // '@store': path.resolve(__dirname, '../src/store'),
      // '@views': path.resolve(__dirname, '../src/views'),
      // '@api': path.resolve(__dirname, '../src/api'),
      // '@types': path.resolve(__dirname, '../src/types'),
    },
  },
  module: {
    rules: [
      {
        test: /\.s?(c|a)ss$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: true,
              sourceMap: true,
              importLoaders: 1,
            },
          },
          'sass-loader',
        ],
        include: /\.module\.s?(c|a)ss$/,
      },
      {
        test: /\.s?css$/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
        exclude: /\.module\.s?(c|a)ss$/,
      },
      // Fonts
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
      // Images
      {
        test: /\.(png|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
      },
      // SVG
      {
        test: /\.svg$/,
        use: [
          {
            loader: '@svgr/webpack',
            options: {
              prettier: false,
              svgo: false,
              svgoConfig: {
                plugins: [{ removeViewBox: false }],
              },
              titleProp: true,
              ref: true,
            },
          },
          'file-loader',
        ],
      },
    ],
  },
  plugins: [
    // ...(skipDLLs
    //   ? []
    //   : [
    //       new webpack.DllReferencePlugin({
    //         context: webpackPaths.dllPath,
    //         manifest: require(manifest),
    //         sourceType: 'var',
    //       }),
    //     ]),

    new webpack.NoEmitOnErrorsPlugin(),

    /**
     * Create global constants which can be configured at compile time.
     *
     * Useful for allowing different behaviour between development builds and
     * release builds
     *
     * NODE_ENV should be production so that modules do not perform certain
     * development checks
     *
     * By default, use 'development' as NODE_ENV. This can be overriden with
     * 'staging', for example, by changing the ENV variables in the npm scripts
     */
    new webpack.EnvironmentPlugin({
      NODE_ENV: 'development',
    }),

    new webpack.LoaderOptionsPlugin({
      debug: true,
    }),

    new ReactRefreshWebpackPlugin(),

    new HtmlWebpackPlugin({
      filename: path.join('index.html'),
      template: path.join(webpackPaths.srcPath, 'index.ejs'),
      minify: {
        collapseWhitespace: true,
        removeAttributeQuotes: true,
        removeComments: true,
      },
      isBrowser: true,
      env: process.env.NODE_ENV,
      isDevelopment: process.env.NODE_ENV !== 'production',
      // nodeModules: webpackPaths.appNodeModulesPath,
    }),
  ],

  node: {
    __dirname: false,
    __filename: false,
  },

  devServer: {
    port,
    compress: true,
    hot: true,
    headers: { 'Access-Control-Allow-Origin': '*' },
    static: {
      publicPath: '/',
    },
    // historyApiFallback: {
    //   verbose: true,
    // },
  },
};

export default merge(baseConfig, configuration);
