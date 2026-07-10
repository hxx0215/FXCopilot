from collections import deque
from json import JSONDecodeError

import requests

from module.base.timer import Timer
from module.exception import ScriptError
from module.logger import logger


class ServerChecker:
    def __init__(self, server: str) -> None:
        self._base: str = 'https://fx-status.pages.dev'
        self._api: str = '/api/force/status'
        
        # 处理服务器名称（直接使用，不需要分割转换）
        self._server: str = server
        
        # 状态缓存（存储最近2次状态）
        self._state: deque = deque(maxlen=2)
        
        # 时间戳相关
        self._timestamp: int = 0
        self._expired: int = 0
        
        # 定时器
        self._timer: Timer = Timer(0)
        
        # 状态标志
        self._recover: bool = False
        self._retry: bool = False
        
        # 立即检查一次
        self.check_now()

    def _load_server(self) -> None:
        """
        获取服务器状态
        设置不可用原因
        如果API有问题会抛出ScriptError
        """
        if self._server == 'disabled':
            self._state.append(True)
            return

        try:
            session = requests.Session()
            session.trust_env = False
            resp = session.get(
                url=f'{self._base}{self._api}',
                timeout=15
            )
            if resp.status_code == 200:
                j = resp.json()
                
                # 从返回数据中找到指定服务器的状态
                server_status = None
                for server_info in j['status']:
                    if server_info['server'] == self._server:
                        server_status = server_info['status']
                        break
                
                if server_status is None:
                    self._state.append(False)
                    raise ScriptError(f'Server "{self._server}" not found in API response!')
                
                if server_status:
                    self._state.append(True)
                    logger.info(f'Server "{self._server}" is available.')
                else:
                    self._state.append(False)
                    logger.info(f'Server "{self._server}" is under maintenance.')

                # 检查API数据更新时间
                if j['updateAt'] > self._timestamp:
                    self._timestamp = j['updateAt']
                    self._expired = 0
                else:
                    self._expired += 1
                    if self._expired > 3:
                        logger.warning(f'Timestamp {self._timestamp} has not been updated for 3 times.')
            else:
                raise ScriptError(f'Get status_code {resp.status_code}. Response is {resp.text}')
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
            logger.error(e)
            logger.error('Timeout while connecting to server checker API.')
            if self._retry:
                self._state.append(False)
            else:
                self._state.append(self.fast_retry())
        except JSONDecodeError:
            self._state.append(False)
            raise ScriptError(f'Response "{resp.text}" seems not to be a JSON.')
        except Exception as e:
            logger.error(e)
            self._state.append(False)
            raise e

    def fast_retry(self) -> bool:
        """
        快速重试机制
        有时国内用户可能无法连接到API，即使网络可用
        因此需要另一个可信的站点来判断网络状态
        这里选择百度
        
        Returns:
            bool: 如果网络可用返回True
        """
        self._retry = True
        try:
            session = requests.Session()
            session.trust_env = False
            _ = session.get('https://www.baidu.com', timeout=5)
            network_available = True
        except Exception as e:
            logger.error(e)
            network_available = False

        logger.attr('network_available', network_available)
        if network_available:
            logger.info('Trigger fast retry.')
            last = self._state.copy()
            for _ in range(3):
                logger.info(f'Retry {_ + 1} times ...')
                self._load_server()
                if self._state[0]:
                    self._retry = False
                    self._state.extend(last)
                    return True

            logger.error('Cannot connect to API. Please check your network or disable server checker.')
            self._retry = False
            self._state.extend(last)
            return False
        else:
            self._retry = False
            logger.error('Network is unavailable. Please check your network status.')
            return False

    def check_now(self) -> None:
        """
        立即检查服务器状态，忽略定时器
        
        如果服务器可用，服务器检查器将保持静默
        否则，定时器将逐渐从2分钟增加到10分钟
        
        如果发生ScriptError，服务器检查器将暂时强制关闭
        """
        try:
            self._load_server()
            if self._state[-1]:
                self._timer.limit = 0
                # 恢复标志：当前状态为True且上一次状态为False
                if not self._state[0]:
                    self._recover = True
            else:
                if self._timer.limit < 600:
                    self._timer.limit += 120
                logger.info(f'Server checker will retry after {self._timer.limit}s')
            self._timer.reset()
        except ScriptError as e:
            logger.warning(str(e))
            logger.warning('There may be something wrong with server checker.')
            logger.warning('Please contact the developer to fix it.')
            logger.warning('Server checker will be temporarily forced off.')
            self.reset()
            self._server = 'disabled'
            self._recover = True
            self._state.append(True)
        except Exception as e:
            raise e

    def is_available(self) -> bool:
        """
        使用缓存返回服务器状态
        
        Returns:
            bool: 如果服务器可用返回True
        """
        if self._timer.limit != 0 and self._timer.reached():
            self.check_now()
        
        return self._state[-1]  # 返回最新的状态

    def wait_until_available(self) -> None:
        """等待服务器可用"""
        while not self.is_available():
            self._timer.wait()
            self.check_now()

    def is_recovered(self) -> bool:
        """
        Returns:
            bool: 如果服务器从不可用状态恢复则返回True
        """
        if len(self._state) < 2:
            self._recover = False
            return False
        
        if self._recover:
            self._recover = False
            return True
        
        return False

    def reset(self) -> None:
        """重置内部状态"""
        self._timestamp = 0
        self._expired = 0
        self._timer.limit = 0
        self._recover = False
