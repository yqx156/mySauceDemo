## Directory
```
SauceDemo/                              # 项目根目录 - SauceDemo自动化测试框架
├── config/                             # 配置模块 - 存放所有配置文件
│   ├── config.py                       # 主配置文件 - 测试数据、URL、浏览器设置等
│   └── __init__.py                     # Python包初始化文件 - 使config成为可导入的包
├── core/                               # 核心模块 - 框架核心功能
│   ├── exceptions.py                   # 自定义异常类 - 登录、购物车、结账等异常定义
│   ├── logger_config.py                # 日志配置 - 日志格式、输出路径、级别设置
│   ├── webdriver_utils.py              # WebDriver工具类 - 浏览器管理、元素操作封装
│   └── __init__.py                     # Python包初始化文件
├── drivers/                            # 浏览器驱动目录 - 存放各种浏览器驱动程序
│   └── edgedriver_win64/               # Edge浏览器驱动(Windows 64位)
│       ├── msedgedriver.exe            # Edge WebDriver可执行文件
│       └── Driver_Notes/               # 驱动说明文档目录
├── logs/                               # 日志输出目录 - 测试执行日志文件(自动生成)
│   └── *.log                           # 日志文件 - 格式:test_execution_YYYYMMDD_HHMMSS.log
├── pages/                              # 页面对象模块 - Page Object Model实现
│   ├── page_objects.py                 # 页面对象类 - 登录页、商品页、购物车页等页面封装
│   └── __init__.py                     # Python包初始化文件
├── reports/                            # 测试报告模块 - 测试结果处理和报告生成
│   ├── test_reporter.py                # 测试报告生成器 - Excel报告、测试结果统计
│   └── __init__.py                     # Python包初始化文件
├── tests/                              # 测试用例模块 - 具体的测试实现
│   ├── test_saucedemo.py               # 主测试文件 - 包含17个完整测试用例
│   └── __init__.py                     # Python包初始化文件
├── test_reports/                       # 测试报告输出目录 - 生成的测试报告文件(自动生成)
│   ├── *.html                          # HTML测试报告 - pytest-html生成的详细报告
│   └── *.xlsx                          # Excel测试报告 - 自定义生成的测试结果统计表
├── conftest.py                         # pytest全局配置 - fixture定义、钩子函数、测试环境配置
├── run_tests.py                        # 测试运行入口 - 主执行脚本，启动测试并生成报告
└── requirements.txt                    # 项目依赖 - Python包依赖列表
```