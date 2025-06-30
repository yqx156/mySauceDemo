"""
测试结果报告模块 - 修复版本
"""
import os
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime
import re

from config import REPORTS_DIR
from core.logger_config import logger

class TestResult:
    """测试结果数据类"""
    
    def __init__(self, test_name="", username="", status="", execution_time="", 
                 error_message="", description=""):
        self.test_name = test_name
        self.username = username
        self.status = status
        self.execution_time = execution_time
        self.error_message = self._clean_error_message(error_message)  # 清理错误信息
        self.description = description
    
    def _clean_error_message(self, error_message):
        """清理错误信息中的特殊字符"""
        if not error_message:
            return ""
        
        # 移除ANSI转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', str(error_message))
        
        # 移除其他特殊字符，保留基本的错误信息
        cleaned = re.sub(r'[^\w\s\-\.\,\:\(\)\[\]\'\"\/\\]', '', cleaned)
        
        # 限制长度，避免Excel单元格过大
        if len(cleaned) > 1000:
            cleaned = cleaned[:1000] + "...(truncated)"
        
        return cleaned
    
    def to_dict(self):
        """转换为字典"""
        return {
            'test_name': self.test_name,
            'username': self.username,
            'status': self.status,
            'execution_time': self.execution_time,
            'error_message': self.error_message,
            'description': self.description
        }

class TestReporter:
    """测试报告生成器"""
    
    def __init__(self):
        self.test_results = []
    
    def add_test_result(self, test_result):
        """添加测试结果"""
        try:
            if isinstance(test_result, TestResult):
                self.test_results.append(test_result)
            elif isinstance(test_result, dict):
                result = TestResult(**test_result)
                self.test_results.append(result)
            else:
                logger.error("无效的测试结果格式")
        except Exception as e:
            logger.error(f"添加测试结果失败: {str(e)}")
    
    def save_results_to_excel(self, filename=None):
        """将测试结果保存到Excel文件"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"saucedemo_test_results_{timestamp}.xlsx"
            
            wb = Workbook()
            ws = wb.active
            ws.title = "测试结果"
            
            # 设置表头
            headers = ["测试用例名称", "用户名", "测试结果", "执行时间", "错误信息", "测试描述"]
            ws.append(headers)
            
            # 设置表头样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            
            # 添加测试结果数据
            for result in self.test_results:
                try:
                    result_dict = result.to_dict() if isinstance(result, TestResult) else result
                    
                    # 确保所有值都是字符串并清理特殊字符
                    row_data = [
                        self._safe_string(result_dict.get('test_name', '')),
                        self._safe_string(result_dict.get('username', '')),
                        self._safe_string(result_dict.get('status', '')),
                        self._safe_string(result_dict.get('execution_time', '')),
                        self._safe_string(result_dict.get('error_message', '')),
                        self._safe_string(result_dict.get('description', ''))
                    ]
                    
                    ws.append(row_data)
                    
                except Exception as e:
                    logger.warning(f"跳过无效的测试结果: {str(e)}")
                    continue
            
            # 设置列宽
            column_widths = [30, 20, 15, 20, 50, 40]
            for col_num, width in enumerate(column_widths, 1):
                ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = width
            
            # 设置数据行样式
            for row_num in range(2, len(self.test_results) + 2):
                for col_num in range(1, len(headers) + 1):
                    try:
                        cell = ws.cell(row=row_num, column=col_num)
                        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                        
                        # 根据测试结果设置颜色
                        if col_num == 3:  # 测试结果列
                            if cell.value == "PASSED":
                                cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                            elif cell.value == "FAILED":
                                cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                    except Exception as e:
                        logger.warning(f"设置单元格样式失败: {str(e)}")
                        continue
            
            # 保存文件
            if not os.path.exists(REPORTS_DIR):
                os.makedirs(REPORTS_DIR)
            
            filepath = os.path.join(REPORTS_DIR, filename)
            wb.save(filepath)
            logger.info(f"测试结果已保存到: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存Excel文件失败: {str(e)}")
            return None
    
    def _safe_string(self, value):
        """安全转换为字符串，移除不支持的字符"""
        try:
            if value is None:
                return ""
            
            # 转换为字符串
            str_value = str(value)
            
            # 移除ANSI转义序列
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            cleaned = ansi_escape.sub('', str_value)
            
            # 移除Excel不支持的控制字符
            cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
            
            # 限制长度
            if len(cleaned) > 500:
                cleaned = cleaned[:500] + "...(内容过长已截断)"
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"字符串清理失败: {str(e)}")
            return "数据格式错误"
    
    def get_test_summary(self):
        """获取测试摘要"""
        total_tests = len(self.test_results)
        if total_tests == 0:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0}
        
        passed_tests = sum(1 for result in self.test_results 
                          if (result.status if isinstance(result, TestResult) else result.get('status')) == "PASSED")
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests) * 100
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": round(pass_rate, 2)
        }
    
    def clear_results(self):
        """清空测试结果"""
        self.test_results.clear()

# 全局测试报告实例
test_reporter = TestReporter()