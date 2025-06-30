"""
根目录conftest.py - 全局pytest配置
"""
import pytest
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.webdriver_utils import WebDriverManager
from reports.test_reporter import test_reporter, TestResult
from core.logger_config import logger
from core.exceptions import TestException

@pytest.fixture(scope="function")
def driver():
    """WebDriver fixture"""
    driver = None
    try:
        driver = WebDriverManager.create_driver()
        yield driver
    except Exception as e:
        logger.error(f"WebDriver初始化失败: {str(e)}")
        pytest.fail(f"WebDriver初始化失败: {str(e)}")
    finally:
        if driver:
            WebDriverManager.close_driver(driver)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果的钩子函数"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        test_name = item.name
        username = item.callspec.params.get('username', '') if hasattr(item, 'callspec') else ''
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

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时保存结果到Excel"""
    try:
        if test_reporter.test_results:
            filepath = test_reporter.save_results_to_excel()
            if filepath:
                summary = test_reporter.get_test_summary()
                logger.info(f"测试摘要: {summary}")
        else:
            logger.warning("没有测试结果需要保存")
    except Exception as e:
        logger.error(f"pytest_sessionfinish执行失败: {str(e)}")