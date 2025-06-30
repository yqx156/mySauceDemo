"""
自定义异常类
"""

class TestException(Exception):
    """自定义测试异常类"""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception
        
    def __str__(self):
        if self.original_exception:
            return f"{super().__str__()} (原始异常: {str(self.original_exception)})"
        return super().__str__()

class LoginException(TestException):
    """登录相关异常"""
    pass

class ElementException(TestException):
    """元素操作相关异常"""
    pass

class CartException(TestException):
    """购物车操作相关异常"""
    pass

class CheckoutException(TestException):
    """结账相关异常"""
    pass

class ProductException(TestException):
    """产品操作相关异常"""
    pass