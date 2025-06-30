"""
SauceDemo网站自动化测试用例 - 完整版本
"""
import pytest
import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from config import USERNAMES, PASSWORD, FIRST_NAME, LAST_NAME, POSTAL_CODE
    from pages.page_objects import LoginPage, InventoryPage, CartPage, CheckoutPage, ProductDetailPage
    from core.exceptions import TestException
    from core.logger_config import logger
except ImportError as e:
    print(f"导入模块失败: {e}")
    print(f"项目根目录: {project_root}")
    raise

class TestSauceDemo:
    """SauceDemo测试类"""
    
    # 1. 登录功能测试
    @pytest.mark.parametrize("username", USERNAMES)
    def test_login_success(self, driver, username):
        """测试用户登录成功"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 2. 登出功能测试
    @pytest.mark.parametrize("username", USERNAMES)
    def test_logout_success(self, driver, username):
        """测试用户登出成功"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.logout()
            assert not login_page.is_login_success(), f"用户 {username} 登出失败"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 3. 添加单个商品到购物车
    @pytest.mark.parametrize("username", USERNAMES)
    def test_add_single_product_to_cart(self, driver, username):
        """测试添加单个商品到购物车"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            cart_count = inventory_page.get_cart_count()
            assert cart_count == 1, f"购物车数量不正确，期望1，实际{cart_count}"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 4. 添加多个商品到购物车
    @pytest.mark.parametrize("username", USERNAMES)
    def test_add_multiple_products_to_cart(self, driver, username):
        """测试添加多个商品到购物车"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.add_product_by_index(1)
            inventory_page.add_product_by_index(2)
            cart_count = inventory_page.get_cart_count()
            assert cart_count == 3, f"购物车数量不正确，期望3，实际{cart_count}"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 5. 添加所有商品到购物车
    @pytest.mark.parametrize("username", USERNAMES)
    def test_add_all_products_to_cart(self, driver, username):
        """测试添加所有商品到购物车"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            products = inventory_page.get_all_products()
            products_count = len(products)
            inventory_page.add_all_products_to_cart()
            cart_count = inventory_page.get_cart_count()
            assert cart_count == products_count, f"购物车数量不正确，期望{products_count}，实际{cart_count}"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 6. 商品排序测试 - 价格从低到高
    @pytest.mark.parametrize("username", USERNAMES)
    def test_sort_products_price_low_to_high(self, driver, username):
        """测试商品按价格从低到高排序"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("lohi")
            
            # 多次尝试获取价格，确保排序生效
            max_retries = 2
            for attempt in range(max_retries):
                products = inventory_page.get_all_products()
                prices = []
                
                for product in products:
                    try:
                        price_text = product.find_element(*inventory_page.PRODUCT_PRICE).text
                        price = float(price_text.replace("$", ""))
                        prices.append(price)
                    except Exception as e:
                        logger.warning(f"获取价格失败: {str(e)}")
                        continue
                
                if len(prices) > 0:
                    sorted_prices = sorted(prices)
                    if prices == sorted_prices:
                        logger.info(f"价格排序正确: {prices}")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试，价格排序不正确，重试... 当前: {prices}, 期望: {sorted_prices}")
                        time.sleep(0.2)  # 等待2秒再重试
                        continue
                    else:
                        # 最后一次尝试失败
                        assert prices == sorted_prices, f"价格排序不正确: 当前{prices}, 期望{sorted_prices}"
                else:
                    assert False, "无法获取任何价格信息"
                    
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")

    # 7. 商品排序测试 - 价格从高到低
    @pytest.mark.parametrize("username", USERNAMES)
    def test_sort_products_price_high_to_low(self, driver, username):
        """测试商品按价格从高到低排序"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("hilo")
            
            # 多次尝试获取价格，确保排序生效
            max_retries = 2
            for attempt in range(max_retries):
                products = inventory_page.get_all_products()
                prices = []
                
                for product in products:
                    try:
                        price_text = product.find_element(*inventory_page.PRODUCT_PRICE).text
                        price = float(price_text.replace("$", ""))
                        prices.append(price)
                    except Exception as e:
                        logger.warning(f"获取价格失败: {str(e)}")
                        continue
                
                if len(prices) > 0:
                    sorted_prices = sorted(prices, reverse=True)
                    if prices == sorted_prices:
                        logger.info(f"价格排序正确: {prices}")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试，价格排序不正确，重试... 当前: {prices}, 期望: {sorted_prices}")
                        time.sleep(0.2)
                        continue
                    else:
                        assert prices == sorted_prices, f"价格排序不正确: 当前{prices}, 期望{sorted_prices}"
                else:
                    assert False, "无法获取任何价格信息"
                    
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 8. 商品排序测试 - 名称A-Z
    @pytest.mark.parametrize("username", USERNAMES)
    def test_sort_products_name_a_to_z(self, driver, username):
        """测试商品按名称A-Z排序"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("az")
            
            # 添加重试机制，确保排序生效
            max_retries = 2
            for attempt in range(max_retries):
                products = inventory_page.get_all_products()
                names = []
                for product in products:
                    try:
                        name = product.find_element(*inventory_page.PRODUCT_NAME).text
                        names.append(name)
                    except Exception as e:
                        logger.warning(f"获取产品名称失败: {str(e)}")
                        continue
                
                if len(names) > 0:
                    sorted_names = sorted(names)
                    if names == sorted_names:
                        logger.info(f"名称排序正确: {names}")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试，名称排序不正确，重试... 当前: {names}, 期望: {sorted_names}")
                        time.sleep(0.2)
                        continue
                    else:
                        assert names == sorted_names, f"名称排序不正确: 当前{names}, 期望{sorted_names}"
                else:
                    assert False, "无法获取任何产品名称"
                    
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 9. 商品排序测试 - 名称Z-A
    @pytest.mark.parametrize("username", USERNAMES)
    def test_sort_products_name_z_to_a(self, driver, username):
        """测试商品按名称Z-A排序"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("za")
            
            # 添加重试机制，确保排序生效
            max_retries = 2
            for attempt in range(max_retries):
                products = inventory_page.get_all_products()
                names = []
                for product in products:
                    try:
                        name = product.find_element(*inventory_page.PRODUCT_NAME).text
                        names.append(name)
                    except Exception as e:
                        logger.warning(f"获取产品名称失败: {str(e)}")
                        continue
                
                if len(names) > 0:
                    sorted_names = sorted(names, reverse=True)
                    if names == sorted_names:
                        logger.info(f"名称排序正确: {names}")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试，名称排序不正确，重试... 当前: {names}, 期望: {sorted_names}")
                        time.sleep(0.2)
                        continue
                    else:
                        assert names == sorted_names, f"名称排序不正确: 当前{names}, 期望{sorted_names}"
                else:
                    assert False, "无法获取任何产品名称"
                    
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 10. 查看购物车
    @pytest.mark.parametrize("username", USERNAMES)
    def test_view_cart(self, driver, username):
        """测试查看购物车"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            assert "cart" in driver.current_url, "未能进入购物车页面"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 11. 从购物车移除商品
    @pytest.mark.parametrize("username", USERNAMES)
    def test_remove_product_from_cart(self, driver, username):
        """测试从购物车移除商品"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.remove_product_from_cart(0)
            
            cart_items = cart_page.get_cart_items()
            assert len(cart_items) == 0, f"购物车商品未被移除，当前数量: {len(cart_items)}"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 12. 继续购物功能
    @pytest.mark.parametrize("username", USERNAMES)
    def test_continue_shopping(self, driver, username):
        """测试继续购物功能"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.continue_shopping()
            assert "inventory" in driver.current_url, "未能返回商品页面"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 13. 查看商品详情
    @pytest.mark.parametrize("username", USERNAMES)
    def test_view_product_details(self, driver, username):
        """测试查看商品详情"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.click_product_image(0)
            assert "inventory-item" in driver.current_url, "未能进入商品详情页"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 14. 从商品详情页返回
    @pytest.mark.parametrize("username", USERNAMES)
    def test_back_to_products_from_details(self, driver, username):
        """测试从商品详情页返回商品列表"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.click_product_image(0)
            
            product_detail_page = ProductDetailPage(driver)
            product_detail_page.back_to_products()
            assert "inventory.html" in driver.current_url, "未能返回商品列表页面"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 15. 完整结账流程
    @pytest.mark.parametrize("username", USERNAMES)
    def test_complete_checkout_flow(self, driver, username):
        """测试完整结账流程"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.checkout()
            
            checkout_page = CheckoutPage(driver)
            checkout_page.fill_checkout_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
            checkout_page.continue_checkout()
            checkout_page.finish_checkout()
            
            assert "checkout-complete" in driver.current_url, "结账流程未完成"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 16. 取消结账流程
    @pytest.mark.parametrize("username", USERNAMES)
    def test_cancel_checkout_flow(self, driver, username):
        """测试取消结账流程"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.checkout()
            
            checkout_page = CheckoutPage(driver)
            checkout_page.cancel_checkout()
            assert "cart" in driver.current_url, "取消结账后未返回购物车"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")
    
    # 17. 验证商品信息准确性
    @pytest.mark.parametrize("username", USERNAMES)
    def test_product_information_accuracy(self, driver, username):
        """测试商品信息的准确性"""
        try:
            login_page = LoginPage(driver)
            login_page.login(username, PASSWORD)
            assert login_page.is_login_success(), f"用户 {username} 登录失败"
            
            inventory_page = InventoryPage(driver)
            product_info = inventory_page.get_product_details(0)
            assert product_info is not None, "无法获取商品信息"
            assert product_info["name"] != "", "商品名称为空"
            assert product_info["desc"] != "", "商品描述为空"
            assert "$" in product_info["price"], "商品价格格式不正确"
        except TestException as e:
            pytest.fail(f"测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"测试意外失败: {str(e)}")
            pytest.fail(f"测试意外失败: {str(e)}")