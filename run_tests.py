"""
测试运行脚本
"""
import pytest
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.logger_config import logger
from reports.test_reporter import test_reporter
from config import REPORTS_DIR

def run_tests():
    """运行测试"""
    logger.info("=" * 60)
    logger.info("开始运行SauceDemo自动化测试")
    logger.info("=" * 60)
    
    # 确保报告目录存在
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    
    # 生成带时间戳的HTML报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report_path = os.path.join(REPORTS_DIR, f"pytest_report_{timestamp}.html")
    
    # pytest运行参数
    pytest_args = [
        "tests/test_saucedemo.py",  # 测试文件
        "-v",  # 详细输出
        "--tb=short",  # 简短的traceback
        "--capture=no",  # 不捕获输出
        f"--html={html_report_path}",  # 生成HTML报告
        "--self-contained-html",  # 生成自包含的HTML文件
    ]
    
    try:
        logger.info(f"HTML报告将保存到: {html_report_path}")
        exit_code = pytest.main(pytest_args)
        
        # 打印测试摘要
        summary = test_reporter.get_test_summary()
        logger.info("=" * 60)
        logger.info("测试执行完成")
        logger.info(f"总测试数: {summary['total']}")
        logger.info(f"通过数: {summary['passed']}")
        logger.info(f"失败数: {summary['failed']}")
        logger.info(f"通过率: {summary['pass_rate']}%")
        logger.info(f"HTML报告已生成: {html_report_path}")
        logger.info("=" * 60)
        
        return exit_code
        
    except Exception as e:
        logger.error(f"运行测试时发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)