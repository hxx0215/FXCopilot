import os
import time
from typing import Iterable

from deploy.Windows.config import DeployConfig
from deploy.Windows.logger import Progress, logger
from deploy.Windows.utils import cached_property, iter_process


class AlasManager(DeployConfig):
    @cached_property
    def alas_folder(self):
        return [
            self.filepath(self.PythonExecutable),
            self.root_filepath
        ]

    @cached_property
    def self_pid(self):
        return os.getpid()

    def list_process(self) -> "list[tuple[int, list[str]]]":
        logger.info('List process')
        process_data = list(iter_process())
        logger.info(f'Found {len(process_data)} processes')
        return process_data

    def iter_process_by_names(self, names, in_alas=False) -> "Iterable[int]":
        """
        Args:
            names (str, list[str]): process name, such as 'alas.exe'
            in_alas (bool): If the output process must in Alas

        Yields:
            pid:
        """
        if not isinstance(names, list):
            names = [names]
        try:
            for pid, cmdline in self.list_process():
                if pid == self.self_pid:
                    continue
                exe = cmdline[0]
                name = os.path.basename(exe)
                if not (name and name in names):
                    continue

                if in_alas:
                    exe = exe.replace(r"\\", "/").replace("\\", "/")
                    for folder in self.alas_folder:
                        if folder in exe:
                            yield pid
                else:
                    yield pid
        except Exception as e:
            logger.info(str(e))
            return False

    def kill_process(self, pid: int):
        self.execute(f'taskkill /f /t /pid {pid}', allow_failure=True, output=False)

    def alas_kill(self):
        import time
        
        logger.hr('Kill existing Alas', 0)
        
        # 首先检查psutil是否可用
        try:
            import psutil
        except ImportError as e:
            logger.error(f'psutil not available: {e}, skipping Alas kill')
            Progress.KillExisting()
            return True
        
        for attempt in range(10):
            logger.info(f'Kill attempt {attempt + 1}/10')
            
            try:
                proc_list = list(self.iter_process_by_names(['python.exe'], in_alas=True))
                if not len(proc_list):
                    logger.info('No existing Alas processes found')
                    Progress.KillExisting()
                    return True
                    
                logger.info(f'Found {len(proc_list)} Alas processes to kill')
                for proc in proc_list:
                    logger.info(f'Killing process: {proc}')
                    self.kill_process(proc)
                
                # 等待进程真正结束
                time.sleep(1)
                
            except Exception as e:
                logger.error(f'Error during Alas kill attempt {attempt + 1}: {e}')

        logger.warning('Unable to kill all existing Alas processes after 10 attempts')
        Progress.KillExisting()
        return False


if __name__ == '__main__':
    self = AlasManager()
    start = time.time()
    self.alas_kill()
    print(time.time() - start)
