"""
重构后的pytest全局配置 - 增加Reset App State功能
"""
import pytest
import sys
import os
from datetime import datetime
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.webdriver_utils import WebDriverManager
from reports.test_reporter import test_reporter, TestResult
from core.logger_config import logger
from core.exceptions import TestException
from config import USERNAMES, PASSWORD

# 全局变量存储当前测试会话信息
current_session = {
    'driver': None,
    'current_user': None,
    'user_index': 0,
    'pages': {}
}

@pytest.fixture(scope="session")
def session_driver():
    """会话级WebDriver fixture - 整个测试会话只创建一次"""
    driver = None
    try:
        driver = WebDriverManager.create_driver()
        current_session['driver'] = driver
        logger.info("会话级WebDriver创建成功")
        yield driver
    except Exception as e:
        logger.error(f"会话级WebDriver初始化失败: {str(e)}")
        pytest.fail(f"会话级WebDriver初始化失败: {str(e)}")
    finally:
        if driver:
            WebDriverManager.close_driver(driver)
            current_session['driver'] = None
            logger.info("会话级WebDriver已关闭")

@pytest.fixture(scope="function")
def user_session(session_driver):
    """用户会话fixture - 管理用户登录状态"""
    from pages.page_objects import LoginPage, InventoryPage
    
    driver = session_driver
    
    # 计算当前应该使用的用户
    user_index = current_session['user_index']
    current_user = USERNAMES[user_index % len(USERNAMES)]
    
    # 检查是否需要切换用户
    if current_session['current_user'] != current_user:
        try:
            # 🔥 如果有当前用户，先重置应用状态再登出
            if current_session['current_user'] is not None:
                try:
                    inventory_page = InventoryPage(driver)
                    
                    # 登出
                    inventory_page.logout()
                    logger.info(f"用户 {current_session['current_user']} 应用状态已重置")
                    logger.info(f"用户 {current_session['current_user']} 已登出")
                    
                except Exception as e:
                    logger.warning(f"重置状态或登出失败: {str(e)}")
                    # 如果重置或登出失败，强制导航到登录页
                    try:
                        from config import BASE_URL
                        driver.get(BASE_URL)
                        time.sleep(0.2)
                    except:
                        pass
            
            # 登录新用户
            login_page = LoginPage(driver)
            login_page.login(current_user, PASSWORD)
            
            if not login_page.is_login_success():
                raise TestException(f"用户 {current_user} 登录失败")
            
            current_session['current_user'] = current_user
            logger.info(f"用户 {current_user} 登录成功")
            
        except Exception as e:
            logger.error(f"用户切换失败: {str(e)}")
            pytest.fail(f"用户切换失败: {str(e)}")
    
    # 返回当前用户信息和driver
    yield {
        'driver': driver,
        'username': current_user,
        'user_index': user_index
    }

def pytest_runtest_setup(item):
    """测试用例设置钩子"""
    # 在每个测试功能的第一个用户测试前重置用户索引
    test_name = item.name.split('[')[0]  # 去除参数化部分
    
    # 如果是新的测试功能，重置用户索引
    if not hasattr(pytest_runtest_setup, 'last_test_name') or pytest_runtest_setup.last_test_name != test_name:
        current_session['user_index'] = 0
        pytest_runtest_setup.last_test_name = test_name
        logger.info(f"开始新测试功能: {test_name}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果的钩子函数"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        test_name = item.name.split('[')[0] if '[' in item.name else item.name
        
        # 获取当前用户名
        username = current_session.get('current_user', '')
        
        status = "PASSED" if rep.passed else "FAILED"
        execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_message = ""
        if rep.failed and rep.longrepr:
            try:
                error_message = str(rep.longrepr)
                if "AssertionError:" in error_message:
                    lines = error_message.split('\n')
                    assertion_lines = [line for line in lines if "AssertionError:" in line or "assert" in line]
                    if assertion_lines:
                        error_message = '\n'.join(assertion_lines[:3])
            except Exception as e:
                error_message = f"错误信息处理失败: {str(e)}"
        
        description = item.function.__doc__ or ""
        
        test_result = TestResult(
            test_name=test_name,
            username=username,
            status=status,
            execution_time=execution_time,
            error_message=error_message,
            description=description
        )
        
        test_reporter.add_test_result(test_result)
        
        # 🔥 每个测试用例完成后，执行应用状态重置
        try:
            if current_session.get('driver') and current_session.get('current_user'):
                from pages.page_objects import InventoryPage
                inventory_page = InventoryPage(current_session['driver'])
                inventory_page.reset_app_state()
                logger.info(f"测试用例 {test_name} 完成后应用状态已重置")
        except Exception as e:
            logger.warning(f"测试用例完成后重置状态失败: {str(e)}")
        
        # 测试完成后，增加用户索引以便下个测试使用下个用户
        current_session['user_index'] += 1

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时保存结果到Excel"""
    try:
        # 🔥 会话结束前最后一次重置应用状态并登出
        if current_session.get('driver') and current_session.get('current_user'):
            try:
                from pages.page_objects import InventoryPage
                inventory_page = InventoryPage(current_session['driver'])
                inventory_page.reset_app_state()
                inventory_page.logout()
                logger.info("测试会话结束，应用状态已重置并登出")
            except Exception as e:
                logger.warning(f"会话结束时重置状态失败: {str(e)}")
        
        if test_reporter.test_results:
            filepath = test_reporter.save_results_to_excel()
            if filepath:
                summary = test_reporter.get_test_summary()
                logger.info(f"测试摘要: {summary}")
        else:
            logger.warning("没有测试结果需要保存")
    except Exception as e:
        logger.error(f"pytest_sessionfinish执行失败: {str(e)}")