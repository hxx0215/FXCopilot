import os
import os.path as path
import re
import typing as t
from dataclasses import dataclass
from urllib.parse import urlparse

from deploy.Windows.config import DeployConfig
from deploy.Windows.logger import logger, Progress
from deploy.Windows.utils import cached_property


@dataclass
class DataDependency:
    name: str
    version: str

    def __post_init__(self):
        # uvicorn[standard] -> uvicorn
        self.name = re.sub(r'\[.*\]', '', self.name)
        # opencv_python -> opencv-python
        self.name = self.name.replace('_', '-').strip()
        # PyYaml -> pyyaml
        self.name = self.name.lower()
        self.version = self.version.strip()
        self.version = re.sub(r'\.0$', '', self.version)

    @cached_property
    def pretty_name(self):
        return f'{self.name}=={self.version}'

    def __str__(self):
        return self.pretty_name

    __repr__ = __str__

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


class PipManager(DeployConfig):
    @cached_property
    def pip(self):
        return f'"{self.python}" -m pip'
    
    @cached_property
    def venv_path(self) -> str:
        """虚拟环境路径"""
        return self.filepath(self.VenvPath)
    
    @cached_property
    def venv_python(self) -> str:
        """虚拟环境中的 Python 路径"""
        if os.name == 'nt':  # Windows
            return self.filepath(path.join(self.VenvPath, 'Scripts/python.exe'))
        else:  # Unix/Linux/macOS
            return self.filepath(path.join(self.VenvPath, 'bin/python'))
    
    @cached_property
    def venv_pip(self) -> str:
        """虚拟环境中的 pip 路径"""
        if os.name == 'nt':  # Windows
            return self.filepath(path.join(self.VenvPath, 'Scripts/pip.exe'))
        else:  # Unix/Linux/macOS
            return self.filepath(path.join(self.VenvPath, 'bin/pip'))
    
    def create_virtualenv(self):
        """创建虚拟环境"""
        logger.hr('Create Virtual Environment', 1)
        
        if os.path.exists(self.venv_path):
            logger.info(f'Virtual environment already exists: {self.venv_path}')
            return
        
        # 确保目录存在
        venv_dir = os.path.dirname(self.venv_path)
        if venv_dir and not os.path.exists(venv_dir):
            os.makedirs(venv_dir, exist_ok=True)
            logger.info(f'Created directory: {venv_dir}')
        
        # 修复引号嵌套问题 - 不需要额外的引号，因为execute方法会处理
        logger.info(f'Creating virtual environment at: {self.venv_path}')
        self.execute(f'{self.python} -m venv {self.venv_path}')
        
        # 升级虚拟环境中的 pip
        logger.info('Upgrading pip in virtual environment')
        self.execute(f'{self.venv_python} -m pip install --upgrade pip')
    
    def _build_pip_args(self):
        """构建 pip 安装参数"""
        arg = []
        if self.PypiMirror:
            mirror = self.PypiMirror
            arg += ['-i', mirror]
            # Trust http mirror or skip ssl verify
            if 'http:' in mirror or not self.SSLVerify:
                arg += ['--trusted-host', urlparse(mirror).hostname]
        elif not self.SSLVerify:
            arg += ['--trusted-host', 'pypi.org']
            arg += ['--trusted-host', 'files.pythonhosted.org']
        arg += ['--disable-pip-version-check']
        return arg

    @cached_property
    def python_site_packages(self) -> str:
        import site
        paths = site.getsitepackages()
        # site-packages should be site-packages folder
        for path in paths:
            if path.endswith('site-packages'):
                return path
        # Otherwise pick first
        return paths[0]

    @cached_property
    def set_installed_dependency(self) -> t.Set[DataDependency]:
        data = []
        regex = re.compile(r'(.*)-(.*).dist-info')
        try:
            for name in os.listdir(self.python_site_packages):
                res = regex.search(name)
                if res:
                    dep = DataDependency(name=res.group(1), version=res.group(2))
                    data.append(dep)
        except FileNotFoundError:
            logger.info(f'Directory not found: {self.python_site_packages}')
        return set(data)

    @cached_property
    def set_required_dependency(self) -> t.Set[DataDependency]:
        data = []
        regex = re.compile('(.*)==(.*)[ ]*#')
        file = self.filepath('./requirements.txt')
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    res = regex.search(line)
                    if res:
                        dep = DataDependency(name=res.group(1), version=res.group(2))
                        data.append(dep)
        except FileNotFoundError:
            logger.info(f'File not found: {file}')
        return set(data)

    @cached_property
    def set_dependency_to_install(self) -> t.Set[DataDependency]:
        """
        A poor dependency comparison, but much much faster than `pip install` and `pip list`
        """
        data = []
        for dep in self.set_required_dependency:
            if dep not in self.set_installed_dependency:
                data.append(dep)
        return set(data)

    def pip_install(self):
        """安装依赖，支持虚拟环境"""
        logger.hr('Update Dependencies', 0)

        if not self.InstallDependencies:
            logger.info('InstallDependencies is disabled, skip')
            Progress.UpdateDependency()
            return

        # 根据配置决定是否使用虚拟环境
        if self.UseVirtualEnv:
            self._pip_install_with_venv()
        else:
            self._pip_install_direct()
    
    def _pip_install_with_venv(self):
        """使用虚拟环境安装依赖"""
        # 1. 创建虚拟环境
        self.create_virtualenv()
        
        # 2. 检查 Python 版本
        logger.hr('Check Virtual Environment Python', 1)
        self.execute(f'{self.venv_python} --version')
        
        # 3. 构建安装参数
        arg = self._build_pip_args()
        
        # 4. 在虚拟环境中安装依赖
        logger.hr('Install Dependencies in Virtual Environment', 1)
        arg_str = ' ' + ' '.join(arg) if arg else ''
        self.execute(f'{self.venv_python} -m pip install -r {self.requirements_file}{arg_str}')
        Progress.UpdateDependency()
    
    def _pip_install_direct(self):
        """直接安装依赖（保持原有逻辑）"""
        if not len(self.set_dependency_to_install):
            logger.info('All dependencies installed')
            Progress.UpdateDependency()
            return
        else:
            logger.info(f'Dependencies to install: {self.set_dependency_to_install}')

        # Install
        logger.hr('Check Python', 1)
        self.execute(f'{self.python} --version')

        arg = self._build_pip_args()

        logger.hr('Update Dependencies', 1)
        arg_str = ' ' + ' '.join(arg) if arg else ''
        self.execute(f'{self.pip} install -r {self.requirements_file}{arg_str}')
        Progress.UpdateDependency()
