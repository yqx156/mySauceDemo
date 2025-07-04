"""
WebDriver工具类
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    WebDriverException,
    StaleElementReferenceException
)

from config import (
    EDGE_DRIVER_PATH, 
    BROWSER_OPTIONS, 
    DEFAULT_WAIT_TIME, 
    IMPLICIT_WAIT_TIME,
    PAGE_LOAD_TIMEOUT
)
from core.exceptions import ElementException
from core.logger_config import logger


"""
"""
class WebDriverManager:
    """WebDriver管理类"""
    
    @staticmethod
    def create_driver():
        """创建WebDriver实例"""
        try:
            options = Options()
            for option in BROWSER_OPTIONS:
                options.add_argument(option)
            
            service = Service(executable_path=EDGE_DRIVER_PATH)
            driver = webdriver.Edge(service=service, options=options) if EDGE_DRIVER_PATH else webdriver.Edge(options=options)
            driver.implicitly_wait(IMPLICIT_WAIT_TIME)
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            
            logger.info("WebDriver创建成功")
            return driver
            
        except WebDriverException as e:
            logger.error(f"WebDriver创建失败: {str(e)}")
            raise ElementException(f"WebDriver创建失败: {str(e)}", e)
        except Exception as e:
            logger.error(f"创建WebDriver时发生意外错误: {str(e)}")
            raise ElementException(f"创建WebDriver时发生意外错误: {str(e)}", e)
    
    @staticmethod
    def close_driver(driver):
        """安全关闭WebDriver"""
        if driver:
            try:
                driver.quit()
                logger.info("WebDriver关闭成功")
            except Exception as e:
                logger.error(f"关闭WebDriver失败: {str(e)}")

class ElementOperations:
    """元素操作工具类"""
    
    @staticmethod
    def wait_for_element(driver, by, value, timeout=DEFAULT_WAIT_TIME):
        """等待元素出现"""
        try:
            wait = WebDriverWait(driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.debug(f"元素找到: {by}={value}")
            return element
        except TimeoutException:
            logger.error(f"等待元素超时: {by}={value}")
            raise ElementException(f"元素未找到: {by}={value}")
    
    @staticmethod
    def wait_for_clickable_element(driver, by, value, timeout=DEFAULT_WAIT_TIME):
        """等待元素可点击"""
        try:
            wait = WebDriverWait(driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            logger.debug(f"元素可点击: {by}={value}")
            return element
        except TimeoutException:
            logger.error(f"等待元素可点击超时: {by}={value}")
            raise ElementException(f"元素不可点击: {by}={value}")
    
    @staticmethod
    def safe_find_element(driver, by, value, timeout=DEFAULT_WAIT_TIME):
        """安全查找元素"""
        try:
            return ElementOperations.wait_for_element(driver, by, value, timeout)
        except ElementException:
            raise
        except Exception as e:
            logger.error(f"查找元素失败: {by}={value}, 错误: {str(e)}")
            raise ElementException(f"查找元素失败: {by}={value}", e)
    
    @staticmethod
    def safe_find_elements(driver, by, value, timeout=DEFAULT_WAIT_TIME):
        """安全查找多个元素"""
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.presence_of_element_located((by, value)))
            elements = driver.find_elements(by, value)
            logger.debug(f"找到 {len(elements)} 个元素: {by}={value}")
            return elements
        except TimeoutException:
            logger.warning(f"未找到元素: {by}={value}")
            return []
        except Exception as e:
            logger.error(f"查找多个元素失败: {by}={value}, 错误: {str(e)}")
            return []
    
    @staticmethod
    def safe_click(driver, element):
        """安全点击元素"""
        try:
            if element.is_enabled() and element.is_displayed():
                element.click()
                time.sleep(0.2)  # 短暂等待
                logger.debug("元素点击成功")
                return True
            else:
                logger.error("元素不可点击")
                raise ElementException("元素不可点击")
        except StaleElementReferenceException:
            logger.error("元素已过期")
            raise ElementException("元素已过期")
        except ElementNotInteractableException:
            logger.error("元素不可交互")
            raise ElementException("元素不可交互")
        except Exception as e:
            logger.error(f"点击元素失败: {str(e)}")
            raise ElementException(f"点击元素失败: {str(e)}", e)
    
    @staticmethod
    def safe_send_keys(element, text):
        """安全输入文本"""
        try:
            if element.is_enabled() and element.is_displayed():
                element.clear()
                element.send_keys(text)
                logger.debug(f"文本输入成功: {text}")
                return True
            else:
                logger.error("输入框不可用")
                raise ElementException("输入框不可用")
        except Exception as e:
            logger.error(f"输入文本失败: {str(e)}")
            raise ElementException(f"输入文本失败: {str(e)}", e)
