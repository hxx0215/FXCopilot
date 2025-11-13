/**
 * But currently electron-builder doesn't support ESM configs
 * @see https://github.com/develar/read-config-file/issues/10
 */

/**
 * @type {() => import('electron-builder').Configuration}
 * @see https://www.electron.build/configuration/configuration
 */
module.exports = async function () {
  const {getVersion} = await import('./version/getVersion.mjs');

  return {
    directories: {
      output: 'dist',
      buildResources: 'buildResources',
    },
    files: ['packages/**/dist/**'],
    extraMetadata: {
      version: getVersion(),
    },
    
    // Windows icon configuration
    win: {
      icon: 'buildResources/icon.ico',
    },
    // macOS icon configuration
    mac: {
      icon: 'buildResources/icon.icns',
    },
    
    // Specify linux target just for disabling snap compilation
    linux: {
      target: 'deb',
    },
  };
};
