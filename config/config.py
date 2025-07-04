"""
测试配置文件
"""

# ========== 测试数据配置 ==========
USERNAMES = [
    "standard_user",
    # "problem_user",
    # "performance_glitch_user",
    # "locked_out_user",
    "visual_user",
    # "error_user",
]

PASSWORD = "secret_sauce"
FIRST_NAME = 'Test'
LAST_NAME = 'User'
POSTAL_CODE = '123456'

# 排序选项
SORT_OPTIONS = ["az", "za", "lohi", "hilo"]

# ========== WebDriver配置 ==========
EDGE_DRIVER_PATH = 'msedgedriver.exe'

# 浏览器选项
BROWSER_OPTIONS = [
    # "--headless",  # 无头模式
    "--disable-gpu", # 禁用GPU加速
    "--no-sandbox", # 禁用沙盒模式
    "--disable-dev-shm-usage", # 禁用/dev/shm使用
    "--window-size=1200,800" # 设置窗口大小
]

# ========== 等待时间配置 ==========
DEFAULT_WAIT_TIME = 0.4
IMPLICIT_WAIT_TIME = 0.4
PAGE_LOAD_TIMEOUT = 30

# ========== 测试报告配置 ==========
REPORTS_DIR = "test_reports"
LOGS_DIR = "logs"

# ========== URL配置 ==========
BASE_URL = "https://www.saucedemo.com/"

# ========== 测试执行配置 ==========
# 是否在用户间切换时重启浏览器 (True: 重启浏览器, False: 只登出登入)
RESTART_BROWSER_BETWEEN_USERS = False
