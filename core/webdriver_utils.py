"""
WebDriver工具类
"""
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from config import EDGE_DRIVER_PATH, BROWSER_OPTIONS, DEFAULT_WAIT_TIME, IMPLICIT_WAIT_TIME, PAGE_LOAD_TIMEOUT
from core.logger_config import logger
from core.exceptions import ElementException

class WebDriverManager:
    """WebDriver管理器"""
    
    @staticmethod
    def create_driver():
        """创建WebDriver实例"""
        try:
            logger.info("开始创建WebDriver实例")
            
            # 配置Edge选项
            options = Options()
            for option in BROWSER_OPTIONS:
                options.add_argument(option)
            
            # 创建Service
            service = Service(EDGE_DRIVER_PATH)
            
            # 创建WebDriver
            driver = webdriver.Edge(service=service, options=options)
            
            # 设置超时
            driver.implicitly_wait(IMPLICIT_WAIT_TIME)
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            
            logger.info("WebDriver创建成功")
            return driver
            
        except Exception as e:
            logger.error(f"创建WebDriver失败: {str(e)}")
            raise ElementException(f"创建WebDriver失败: {str(e)}", e)
    
    @staticmethod
    def close_driver(driver):
        """关闭WebDriver"""
        try:
            if driver:
                driver.quit()
                logger.info("WebDriver已关闭")
        except Exception as e:
            logger.warning(f"关闭WebDriver时出现异常: {str(e)}")

class ElementOperations:
    """元素操作类"""
    
    def safe_find_element(self, driver, by, value, timeout=DEFAULT_WAIT_TIME):
        """安全查找元素"""
        try:
            wait = WebDriverWait(driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.debug(f"成功找到元素: {by}={value}")
            return element
        except TimeoutException:
            logger.error(f"查找元素超时: {by}={value}")
            raise ElementException(f"查找元素超时: {by}={value}")
        except Exception as e:
            logger.error(f"查找元素失败: {by}={value}, 错误: {str(e)}")
            raise ElementException(f"查找元素失败: {by}={value}", e)
    
    def safe_find_elements(self, driver, by, value, timeout=DEFAULT_WAIT_TIME):
        """安全查找多个元素"""
        try:
            wait = WebDriverWait(driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            logger.debug(f"成功找到 {len(elements)} 个元素: {by}={value}")
            return elements
        except TimeoutException:
            logger.warning(f"查找元素超时: {by}={value}")
            return []
        except Exception as e:
            logger.error(f"查找元素失败: {by}={value}, 错误: {str(e)}")
            return []
    
    def safe_click(self, driver, element, timeout=DEFAULT_WAIT_TIME):
        """安全点击元素"""
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.element_to_be_clickable(element))
            element.click()
            logger.debug("元素点击成功")
            time.sleep(0.1)  # 短暂等待
        except Exception as e:
            logger.error(f"点击元素失败: {str(e)}")
            raise ElementException(f"点击元素失败: {str(e)}", e)
    
    def safe_send_keys(self, element, text):
        """安全输入文本"""
        try:
            element.clear()
            element.send_keys(text)
            logger.debug(f"文本输入成功: {text}")
        except Exception as e:
            logger.error(f"输入文本失败: {str(e)}")
            raise ElementException(f"输入文本失败: {str(e)}", e)
    
    def safe_get_text(self, element):
        """安全获取元素文本"""
        try:
            text = element.text
            logger.debug(f"获取文本成功: {text}")
            return text
        except Exception as e:
            logger.error(f"获取文本失败: {str(e)}")
            raise ElementException(f"获取文本失败: {str(e)}", e)