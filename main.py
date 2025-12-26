"""
校园网自动连接脚本
支持有线/无线网络检测和浏览器自动化认证
"""

import time
import logging
import sys
import os
import socket
import argparse
from enum import Enum
from typing import Tuple, Optional

# 浏览器自动化相关
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 网络检测相关
import psutil
import pywifi
from pywifi import const

DEFAULT_USER_NAME = "xxx" # 这里写你的学号
DEFAULT_PASSWD = "xxx" # 这里写你的密码


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


class NetworkStatus(Enum):
    """网络状态枚举"""
    CONNECTED = "已连接互联网"
    CAMPUS_ONLY = "仅连接校园网（未认证）"
    NO_NETWORK = "未连接任何网络"


class NetworkType(Enum):
    """网络类型枚举"""
    WIRED = "有线网络"
    WIRELESS = "无线网络"
    UNKNOWN = "未知"


class NetworkDetector:
    """网络检测器"""
    
    @staticmethod
    def check_internet() -> bool:
        """检查互联网连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect(("8.8.8.8", 53))
            sock.close()
            return True
        except:
            return False
    
    @staticmethod
    def check_campus_network() -> bool:
        """检查校园网连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("10.10.9.9", 80))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def get_network_type() -> Tuple[NetworkType, str]:
        """获取网络类型和接口名称"""
        try:
            # 获取网络接口
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            # 检查有线网络
            wired_keywords = ['以太网', 'Ethernet', 'eth', 'enp', 'eno']
            for iface_name, iface_addrs in interfaces.items():
                if iface_name in stats and stats[iface_name].isup:
                    if any(keyword in iface_name for keyword in wired_keywords):
                        # 检查是否有IPv4地址
                        for addr in iface_addrs:
                            if addr.family == socket.AF_INET:
                                return NetworkType.WIRED, iface_name
            
            # 检查无线网络
            wifi_keywords = ['Wi-Fi', 'WLAN', 'wlan', 'wlp', '无线']
            for iface_name, iface_addrs in interfaces.items():
                if iface_name in stats and stats[iface_name].isup:
                    if any(keyword in iface_name for keyword in wifi_keywords):
                        for addr in iface_addrs:
                            if addr.family == socket.AF_INET:
                                return NetworkType.WIRELESS, iface_name
            
            return NetworkType.UNKNOWN, ""
            
        except Exception as e:
            logger.error(f"获取网络类型失败: {e}")
            return NetworkType.UNKNOWN, ""
    
    @staticmethod
    def get_network_status() -> NetworkStatus:
        """获取网络状态"""
        has_internet = NetworkDetector.check_internet()
        has_campus = NetworkDetector.check_campus_network()
        
        if has_internet:
            return NetworkStatus.CONNECTED
        elif has_campus:
            return NetworkStatus.CAMPUS_ONLY
        else:
            return NetworkStatus.NO_NETWORK


class WiFiConnector:
    """Wi-Fi连接器"""
    
    def __init__(self, ssid: str = "Shu(ForAll)"):
        self.ssid = ssid
        self.wifi = pywifi.PyWiFi()
    
    def connect(self) -> bool:
        """连接Wi-Fi"""
        try:
            if not self.wifi.interfaces():
                logger.error("未找到Wi-Fi接口")
                return False
            
            iface = self.wifi.interfaces()[0]
            
            # 断开当前连接
            iface.disconnect()
            time.sleep(1)
            
            # 创建配置
            profile = pywifi.Profile()
            profile.ssid = self.ssid
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_NONE)
            profile.cipher = const.CIPHER_TYPE_NONE
            
            # 应用配置
            iface.remove_all_network_profiles()
            tmp_profile = iface.add_network_profile(profile)
            iface.connect(tmp_profile)
            
            # 等待连接
            for _ in range(10):
                time.sleep(1)
                if iface.status() == const.IFACE_CONNECTED:
                    logger.info(f"已连接到 Wi-Fi: {self.ssid}")
                    return True
            
            logger.error(f"连接Wi-Fi超时: {self.ssid}")
            return False
            
        except Exception as e:
            logger.error(f"连接Wi-Fi失败: {e}")
            return False


class BrowserAuthenticator:
    """浏览器认证器"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.driver = None
    
    def init_browser(self, headless: bool = False) -> bool:
        """初始化浏览器"""
        try:
            options = webdriver.EdgeOptions()
            if headless:
                options.add_argument('--headless')
            
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Edge(options=options)
            self.driver.implicitly_wait(5)
            
            logger.info("浏览器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            return False
    
    def perform_login(self) -> Tuple[bool, str]:
        """执行登录"""
        try:
            # 访问登录页面
            self.driver.get("http://10.10.9.9")
            time.sleep(2)
            
            # 检查是否已登录
            try:
                user_element = self.driver.find_element(By.CSS_SELECTOR, "#userId")
                if user_element and user_element.text == self.username:
                    return True, f"用户 {self.username} 已登录"
            except:
                pass
            
            # 填写登录表单
            self.driver.execute_script(f"document.getElementById(arguments[0]).value = arguments[1];", "username", self.username)
            self.driver.execute_script(f"document.getElementById(arguments[0]).value = arguments[1];", "pwd", self.password)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "#loginLink")
            login_button.click()
            
            logger.info("已提交登录信息")
            time.sleep(3)
            
            # 验证登录结果
            try:
                user_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#userId"))
                )
                if user_element.text == self.username:
                    return True, "登录成功"
            except:
                return False, "登录验证失败"
                
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False, str(e)
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except:
                pass


class CampusNetworkManager:
    """校园网管理器"""
    
    def __init__(self, username: str, password: str, ssid: str = "Shu(ForAll)"):
        self.username = username
        self.password = password
        self.ssid = ssid
        
        # 初始化组件
        self.detector = NetworkDetector()
        self.wifi_connector = WiFiConnector(ssid)
        self.authenticator = BrowserAuthenticator(username, password)
    
    def check_and_connect(self, headless: bool = False) -> bool:
        """检查并连接网络"""
        logger.info("=" * 50)
        logger.info("校园网连接开始")
        logger.info("=" * 50)
        
        # 1. 检查当前网络状态
        status = self.detector.get_network_status()
        logger.info(f"当前网络状态: {status.value}")
        
        if status == NetworkStatus.CONNECTED:
            logger.info("已连接互联网，无需操作")
            return True
        
        # 2. 获取网络类型
        net_type, iface_name = self.detector.get_network_type()
        logger.info(f"网络类型: {net_type.value}, 接口: {iface_name}")
        
        # 3. 处理不同状态
        if status == NetworkStatus.CAMPUS_ONLY:
            logger.info("检测到校园网，尝试认证...")
            return self._try_authentication(headless)
        
        elif status == NetworkStatus.NO_NETWORK:
            logger.info("未检测到网络，尝试连接...")
            return self._establish_connection(headless)
        
        return False
    
    def _try_authentication(self, headless: bool) -> bool:
        """尝试认证"""
        # 初始化浏览器
        if not self.authenticator.init_browser(headless):
            logger.error("浏览器初始化失败")
            return False
        
        try:
            # 执行登录
            success, message = self.authenticator.perform_login()
            
            if success:
                logger.info(f"{message}")
                
                # 验证连接
                time.sleep(2)
                if NetworkDetector.check_internet():
                    logger.info("认证成功，已连接互联网")
                    return True
                else:
                    logger.warning("认证完成但网络连接异常")
                    return False
            else:
                logger.error(f"{message}")
                return False
        except Exception as e:
            logger.error(f"认证过程中发生错误: {e}")
            return False
    
    def _establish_connection(self, headless: bool) -> bool:
        """建立网络连接"""
        logger.info("尝试连接网络...")
        
        # 检查网络类型
        net_type, iface_name = self.detector.get_network_type()
        
        if net_type == NetworkType.WIRED:
            logger.info("检测到有线网络，等待连接...")
            # 有线网络通常自动获取IP
            time.sleep(5)
            
            if NetworkDetector.check_campus_network():
                logger.info("有线网络连接成功，尝试认证...")
                return self._try_authentication(headless)
        
        # 尝试连接Wi-Fi
        logger.info("尝试连接Wi-Fi...")
        if self.wifi_connector.connect():
            logger.info("Wi-Fi连接成功，等待获取IP...")
            time.sleep(5)
            
            if NetworkDetector.check_campus_network():
                logger.info("Wi-Fi网络就绪，尝试认证...")
                return self._try_authentication(headless)
        
        logger.error("无法建立网络连接")
        return False
    
    def cleanup(self):
        """清理资源"""
        self.authenticator.close()

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="校园网自动连接工具")
    parser.add_argument("-u", "--username", type=str, default=DEFAULT_USER_NAME, help="校园网账号")
    parser.add_argument("-p", "--password", type=str, default=DEFAULT_PASSWD, help="校园网密码")
    parser.add_argument("-s", "--ssid", default="Shu(ForAll)", help="Wi-Fi网络名称")
    parser.add_argument("--headless", action="store_true", default=False, help="无头模式")
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 创建管理器
    manager = CampusNetworkManager(
        username=args.username,
        password=args.password,
        ssid=args.ssid
    )
    
    try:
        success = manager.check_and_connect(headless=args.headless)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        return 130
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        return 1
    finally:
        manager.cleanup()


if __name__ == "__main__":
    sys.exit(main())