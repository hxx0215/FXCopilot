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
    appId: 'com.fxcopilot.app',
    productName: 'FXCopilot',
    directories: {
      output: 'dist',
      buildResources: 'buildResources',
    },
    files: ['packages/**/dist/**'],
    // Copy python backend and resources next to the executable so the path resolver can find ./config, ./module, etc.
    extraFiles: [
      {
        from: '..',
        to: '.',
        filter: [
          'assets/**',
          'bin/**',
          'config/**',
          'deploy/**',
          'module/**',
          'tasks/**',
          'requirements.txt',
          'requirements-in.txt',
          'uv-requirements.txt',
          'gui.py',
          'installer.py',
          'console.bat',
          'fxc.py',
        ],
      },
    ],
    extraMetadata: {
      version: getVersion(),
    },

    win: {
      target: [
        {target: 'nsis', arch: ['x64']},
        {target: 'portable', arch: ['x64']},
      ],
      artifactName: '${productName}-${version}-${os}-${arch}.${ext}',
    },
    nsis: {
      oneClick: true,
      perMachine: false,
      allowToChangeInstallationDirectory: false,
      deleteAppDataOnUninstall: false,
    },

    // Specify linux target just for disabling snap compilation
    linux: {
      target: 'deb',
    },
  };
};
