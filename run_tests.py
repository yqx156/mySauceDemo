"""
重构后的测试运行入口 - 使用pytest.main()优化版本
"""
import os
import sys
import pytest
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.logger_config import logger

def run_tests():
    """运行测试套件"""
    try:
        logger.info("=" * 80)
        logger.info("开始执行SauceDemo自动化测试 - 重构优化版本")
        logger.info("=" * 80)
        
        # 创建测试报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 生成HTML报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = os.path.join(reports_dir, f"test_report_{timestamp}.html")
        
        # 构建pytest参数
        pytest_args = [
            "tests/test_saucedemo.py",     # 测试文件路径
            "-v",                          # 详细输出
            "--tb=short",                  # 简短的错误信息
            f"--html={html_report}",       # HTML报告
            "--self-contained-html",       # 自包含的HTML
            "--capture=no",                # 不捕获输出，实时显示日志
            "--strict-markers",            # 严格标记模式
            "--disable-warnings",          # 禁用警告（可选）
        ]
        
        logger.info(f"执行参数: {' '.join(pytest_args)}")
        logger.info("测试模式：优化版本 - 每个功能测试所有用户，减少浏览器开关次数")
        
        # 使用pytest.main()执行测试
        exit_code = pytest.main(pytest_args)
        
        logger.info("=" * 80)
        if exit_code == 0:
            logger.info("✅ 所有测试执行完成并通过！")
        elif exit_code == 1:
            logger.info("⚠️  测试执行完成，但有部分测试失败")
        elif exit_code == 2:
            logger.info("❌ 测试执行被中断或配置错误")
        elif exit_code == 3:
            logger.info("❌ 内部错误")
        elif exit_code == 4:
            logger.info("❌ pytest使用错误")
        elif exit_code == 5:
            logger.info("❌ 没有找到测试用例")
        else:
            logger.info(f"❓ 测试完成，退出代码: {exit_code}")
            
        logger.info(f"📊 HTML报告已生成: {html_report}")
        logger.info("📈 检查 test_reports/ 目录获取详细的Excel测试报告")
        logger.info("=" * 80)
        
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"测试运行失败: {str(e)}")
        return False

def run_tests_with_custom_options(**kwargs):
    """
    带自定义选项运行测试
    
    参数:
        verbose (bool): 是否显示详细输出，默认True
        capture (str): 输出捕获模式，'no'|'sys'|'fd'，默认'no' 
        tb_style (str): 错误信息样式，'short'|'long'|'line'|'native'，默认'short'
        markers (list): 要运行的标记列表
        keywords (str): 关键字表达式过滤测试
        maxfail (int): 最大失败数，达到后停止测试
        html_report (bool): 是否生成HTML报告，默认True
    """
    try:
        logger.info("=" * 80)
        logger.info("开始执行SauceDemo自动化测试 - 自定义配置")
        logger.info("=" * 80)
        
        # 创建测试报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 构建基础pytest参数
        pytest_args = ["tests/test_saucedemo.py"]
        
        # 处理详细输出
        if kwargs.get('verbose', True):
            pytest_args.append("-v")
        
        # 处理错误信息样式
        tb_style = kwargs.get('tb_style', 'short')
        pytest_args.append(f"--tb={tb_style}")
        
        # 处理输出捕获
        capture = kwargs.get('capture', 'no')
        pytest_args.append(f"--capture={capture}")
        
        # 处理HTML报告
        if kwargs.get('html_report', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_report = os.path.join(reports_dir, f"test_report_{timestamp}.html")
            pytest_args.extend([f"--html={html_report}", "--self-contained-html"])
        
        # 处理标记过滤
        markers = kwargs.get('markers')
        if markers:
            if isinstance(markers, list):
                marker_expr = " or ".join(markers)
            else:
                marker_expr = str(markers)
            pytest_args.extend(["-m", marker_expr])
        
        # 处理关键字过滤
        keywords = kwargs.get('keywords')
        if keywords:
            pytest_args.extend(["-k", keywords])
        
        # 处理最大失败数
        maxfail = kwargs.get('maxfail')
        if maxfail:
            pytest_args.extend(["--maxfail", str(maxfail)])
        
        # 添加其他常用选项
        pytest_args.extend([
            "--strict-markers",
            "--disable-warnings"
        ])
        
        logger.info(f"执行参数: {' '.join(pytest_args)}")
        
        # 执行测试
        exit_code = pytest.main(pytest_args)
        
        logger.info("=" * 80)
        logger.info(f"测试执行完成，退出代码: {exit_code}")
        logger.info("=" * 80)
        
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"自定义测试运行失败: {str(e)}")
        return False

def run_specific_test(test_name):
    """
    运行特定的测试用例
    
    参数:
        test_name (str): 测试用例名称，例如 "test_01_login_success"
    """
    try:
        logger.info(f"运行特定测试: {test_name}")
        
        pytest_args = [
            "tests/test_saucedemo.py",
            "-v",
            "--tb=short",
            "--capture=no",
            "-k", test_name
        ]
        
        exit_code = pytest.main(pytest_args)
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"运行特定测试失败: {str(e)}")
        return False

def run_tests_by_marker(marker):
    """
    根据标记运行测试
    
    参数:
        marker (str): pytest标记，例如 "smoke", "regression"
    """
    try:
        logger.info(f"运行标记为 '{marker}' 的测试")
        
        pytest_args = [
            "tests/test_saucedemo.py",
            "-v",
            "--tb=short",
            "--capture=no",
            "-m", marker
        ]
        
        exit_code = pytest.main(pytest_args)
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"运行标记测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "help":
                print("\n可用命令:")
                print("  python run_tests.py              - 运行所有测试")
                print("  python run_tests.py help         - 显示帮助信息")
                print("  python run_tests.py quick        - 快速运行（最多失败3次后停止）")
                print("  python run_tests.py login        - 只运行登录相关测试")
                print("  python run_tests.py cart         - 只运行购物车相关测试")
                print("  python run_tests.py checkout     - 只运行结账相关测试")
                print("  python run_tests.py sort         - 只运行排序相关测试")
                print("\n示例:")
                print("  python run_tests.py quick")
                print("  python run_tests.py login")
                sys.exit(0)
            
            elif command == "quick":
                # 快速测试模式：最多3次失败后停止
                success = run_tests_with_custom_options(
                    maxfail=3,
                    tb_style='line'
                )
            
            elif command == "login":
                # 只运行登录相关测试
                success = run_specific_test("login")
            
            elif command == "cart":
                # 只运行购物车相关测试
                success = run_specific_test("cart")
            
            elif command == "checkout":
                # 只运行结账相关测试
                success = run_specific_test("checkout")
            
            elif command == "sort":
                # 只运行排序相关测试
                success = run_specific_test("sort")
            
            else:
                print(f"未知命令: {command}")
                print("使用 'python run_tests.py help' 查看可用命令")
                sys.exit(1)
        else:
            # 默认运行所有测试
            success = run_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        sys.exit(1)