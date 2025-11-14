import {alasPath, getPythonPath} from '/@/config';
import logger from '/@/logger';
import {PythonShell, Options} from 'python-shell'
const treeKill = require('tree-kill');

export class PyShell extends PythonShell {
  constructor(script: string, args: Array<string> = [], install: boolean = false) {
    const pythonPath = getPythonPath(install)
    const options: Options = {
      mode: 'text',
      args: args,
      pythonPath,
      scriptPath: alasPath,
    };
    logger.info(`${pythonPath} ${script} ${args}`);
    super(script, options);
  }

  on(event: string, listener: (...args: any[]) => void): this {
    this.removeAllListeners(event);
    super.on(event, listener);
    return this;
  }

  kill(callback: (...args: any[]) => void): this {
    if (process.platform === 'win32') {
      console.log('will be kill later');
    } else {
      treeKill(this.childProcess.pid, 'SIGTERM', callback);
    }
    return this;
  }

  childPid(): number| undefined {
    return this.childProcess.pid;
  }
}
