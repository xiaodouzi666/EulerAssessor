import path from 'path';

const rootPath = path.join(__dirname, '../');

const distOuputPath = path.join(rootPath, 'dist');
const srcPath = path.join(rootPath, 'src');
const srcNodeModulesPath = path.join(srcPath, 'node_modules');

export default {
  rootPath,
  srcPath,
  srcNodeModulesPath,
  distOuputPath,
};
