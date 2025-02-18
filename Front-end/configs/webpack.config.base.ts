/**
 * Base webpack config used across other specific configs
 */
import path from 'path';
import webpack from 'webpack';
import TsconfigPathsPlugins from 'tsconfig-paths-webpack-plugin';
import webpackPaths from './webpack.paths';
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

// const TerserPlugin = require('terser-webpack-plugin');
// const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const configuration: webpack.Configuration = {
  stats: 'errors-only',
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  module: {
    rules: [
      {
        test: /\.[jt]sx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'ts-loader',
          options: {
            // Remove this line to enable type checking in webpack builds
            transpileOnly: true,
            compilerOptions: {
              module: 'esnext',
            },
          },
        },
      },
    ],
  },
  entry: [path.join(webpackPaths.srcPath, 'index.tsx')],
  output: {
    path: webpackPaths.distOuputPath,
  },
  /**
   * Determine the array of extensions that should be used to resolve modules.
   */
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
    },
    extensions: ['.js', '.jsx', '.json', '.ts', '.tsx'],
    // modules: [webpackPaths.srcPath, 'node_modules'],
    // There is no need to add aliases here, the paths in tsconfig get mirrored
    plugins: [new TsconfigPathsPlugins()],
  },

  plugins: [
    // new Dotenv(),
    // new MiniCssExtractPlugin(),
    new webpack.ProgressPlugin(),
    // new BundleAnalyzerPlugin(),
    new webpack.EnvironmentPlugin({
      NODE_ENV: 'production',
    }),
  ],
  // optimization: {
  //   minimize: true,
  //   minimizer: [new TerserPlugin()],
  // },
};

export default configuration;
