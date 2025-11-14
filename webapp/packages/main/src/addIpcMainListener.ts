import type {CoreService} from '/@/coreService';
import type {BrowserWindow} from 'electron';
import {app, ipcMain, nativeTheme} from 'electron';
import {
  ELECTRON_THEME,
  INSTALLER_READY,
  PAGE_ERROR,
  WINDOW_READY,
} from '@common/constant/eventNames';
import {ThemeObj} from '@common/constant/theme';
import logger from '/@/logger';
import { pythonPath } from './config';
import { spawn } from 'child_process';
import { join } from 'path';

export const addIpcMainListener = async (mainWindow: BrowserWindow, coreService: CoreService) => {
  // Minimize, maximize, close window.
  ipcMain.on('window-tray', function () {
    mainWindow?.hide();
  });
  ipcMain.on('window-minimize', function () {
    mainWindow?.minimize();
  });
  ipcMain.on('window-maximize', function () {
    mainWindow?.isMaximized() ? mainWindow?.restore() : mainWindow?.maximize();
  });
  ipcMain.on('window-close', function () {
    coreService?.kill();
    mainWindow?.close();
    app.quit();
  });
  let canQuit = false;
  app.on('before-quit', async e => {
    if (canQuit) {
      return;
    }
    e.preventDefault();
    const pids = await coreService.listPids();
    if (process.platform === 'win32' && pids && pids.length > 0) {
      try {
        const terminateScriptPath = join(process.cwd(), 'terminate.py');
        const pythonProcess = spawn(pythonPath, [terminateScriptPath, ...pids.map(String)], {
          detached: true, 
          stdio: 'pipe',
        });
        pythonProcess.unref();
        logger.info(`已启动独立的Python进程用于终止PID: ${pids.join(', ')}`);
      } catch (error) {
        console.error('启动terminate.py时出错:', error);
      } finally {
        canQuit = true;
      }
    } else {
      canQuit = true;
    }
    app.quit();
  });

  ipcMain.on(WINDOW_READY, async function (_, args) {
    logger.info('-----WINDOW_READY-----');
    args && (await coreService.run());
  });

  ipcMain.on(INSTALLER_READY, function () {
    logger.info('-----INSTALLER_READY-----');
    coreService.next();
  });

  ipcMain.on(ELECTRON_THEME, (_, args) => {
    logger.info('-----ELECTRON_THEME-----');
    nativeTheme.themeSource = ThemeObj[args];
  });

  ipcMain.on(PAGE_ERROR, (_, args) => {
    logger.info('-----PAGE_ERROR-----');
    logger.error(args);
  });
};
