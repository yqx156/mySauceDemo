"""
页面对象模型
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from core.webdriver_utils import ElementOperations
from core.exceptions import LoginException, ProductException, CartException, CheckoutException
from core.logger_config import logger
from config import BASE_URL

class BasePage:
    """页面基类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.element_ops = ElementOperations()
    
    def navigate_to(self, url):
        """导航到指定URL"""
        try:
            self.driver.get(url)
            logger.info(f"导航到: {url}")
        except Exception as e:
            logger.error(f"导航失败: {str(e)}")
            raise

class LoginPage(BasePage):
    """登录页面"""
    
    # 页面元素定位器
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    
    def __init__(self, driver):
        super().__init__(driver)
        # 只有当前页面不是登录页时才导航
        if "saucedemo.com" not in self.driver.current_url or "inventory" in self.driver.current_url:
            self.navigate_to(BASE_URL)
    
    def login(self, username, password):
        """登录功能"""
        try:
            logger.info(f"开始登录用户: {username}")
            
            username_field = self.element_ops.safe_find_element(self.driver, *self.USERNAME_INPUT)
            password_field = self.element_ops.safe_find_element(self.driver, *self.PASSWORD_INPUT)
            login_button = self.element_ops.safe_find_element(self.driver, *self.LOGIN_BUTTON)
            
            self.element_ops.safe_send_keys(username_field, username)
            self.element_ops.safe_send_keys(password_field, password)
            self.element_ops.safe_click(self.driver, login_button)
            
            time.sleep(1)  # 等待页面跳转
            logger.info(f"用户 {username} 登录操作完成")
            
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            raise LoginException(f"登录失败: {str(e)}", e)
    
    def is_login_success(self):
        """检查登录是否成功"""
        try:
            return "inventory" in self.driver.current_url
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return False
    
    def get_error_message(self):
        """获取错误消息"""
        try:
            error_element = self.element_ops.safe_find_element(self.driver, *self.ERROR_MESSAGE)
            return error_element.text
        except:
            return ""

class InventoryPage(BasePage):
    """商品页面"""
    
    # 页面元素定位器
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    RESET_APP_STATE_LINK = (By.ID, "reset_sidebar_link")  # 🔥 新增：重置应用状态链接
    MENU_CLOSE_BUTTON = (By.ID, "react-burger-cross-btn")  # 🔥 新增：关闭菜单按钮
    SORT_DROPDOWN = (By.CSS_SELECTOR, "select[data-test='product-sort-container']")
    PRODUCTS = (By.CLASS_NAME, "inventory_item")
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_item_name")
    PRODUCT_DESC = (By.CLASS_NAME, "inventory_item_desc")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_item_price")
    ADD_TO_CART_BUTTON = (By.XPATH, "//button[contains(text(),'Add to cart')]")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    PRODUCT_IMAGE_LINK = (By.CSS_SELECTOR, ".inventory_item_img a")
    
    # def reset_app_state(self):
    #     """🔥 新增：重置应用状态功能"""
    #     try:
    #         logger.info("开始重置应用状态")
            
    #         # 检查当前是否在inventory页面，如果不在则先导航过去
    #         if "inventory" not in self.driver.current_url:
    #             self.driver.get(BASE_URL + "inventory.html")
    #             time.sleep(0.2)
            
    #         # 1. 点击菜单按钮打开侧边栏
    #         menu_button = self.element_ops.safe_find_element(self.driver, *self.MENU_BUTTON)
    #         self.element_ops.safe_click(self.driver, menu_button)
            
    #         time.sleep(0.2)  # 等待菜单打开
            
    #         # 2. 点击Reset App State链接
    #         reset_link = self.element_ops.safe_find_element(self.driver, *self.RESET_APP_STATE_LINK)
    #         self.element_ops.safe_click(self.driver, reset_link)
            
    #         time.sleep(0.2)  # 等待重置完成
            
    #         # 3. 关闭菜单（点击X按钮）
    #         try:
    #             close_button = self.element_ops.safe_find_element(self.driver, *self.MENU_CLOSE_BUTTON, timeout=3)
    #             self.element_ops.safe_click(self.driver, close_button)
    #             time.sleep(0.3)
    #         except Exception as e:
    #             logger.warning(f"关闭菜单失败，尝试点击页面其他区域: {str(e)}")
    #             # 如果关闭按钮点击失败，尝试点击页面其他区域来关闭菜单
    #             try:
    #                 self.driver.find_element(By.CLASS_NAME, "inventory_container").click()
    #                 time.sleep(0.3)
    #             except:
    #                 pass
            
    #         logger.info("应用状态重置完成")
            
    #     except Exception as e:
    #         logger.error(f"重置应用状态失败: {str(e)}")
    #         # 重置失败不应该导致测试失败，只记录警告
    #         logger.warning("应用状态重置失败，继续执行后续操作")
    
    def logout(self):
        """登出功能"""
        try:
            logger.info("开始登出操作")
            
            # 检查当前是否在inventory页面，如果不在则先导航过去
            if "inventory" not in self.driver.current_url:
                self.driver.get(BASE_URL + "inventory.html")
                time.sleep(0.1)
            
            menu_button = self.element_ops.safe_find_element(self.driver, *self.MENU_BUTTON)
            self.element_ops.safe_click(self.driver, menu_button)
            
            time.sleep(0.1)  # 等待菜单打开
            logger.info("开始重置应用状态")
            reset_link = self.element_ops.safe_find_element(self.driver, *self.RESET_APP_STATE_LINK)
            self.element_ops.safe_click(self.driver, reset_link)
            logger.info("应用状态重置完成")
            time.sleep(0.1)  # 等待重置完成
            logout_link = self.element_ops.safe_find_element(self.driver, *self.LOGOUT_LINK)
            self.element_ops.safe_click(self.driver, logout_link)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("登出操作完成")
            
        except Exception as e:
            logger.error(f"登出失败: {str(e)}")
            raise LoginException(f"登出失败: {str(e)}", e)
    
    def sort_products(self, sort_value):
        """排序商品"""
        try:
            logger.info(f"开始商品排序: {sort_value}")
            
            sort_dropdown = self.element_ops.safe_find_element(self.driver, *self.SORT_DROPDOWN)
            select = Select(sort_dropdown)
            select.select_by_value(sort_value)
            
            time.sleep(0.2)  # 等待排序生效
            logger.info(f"商品排序完成: {sort_value}")
            
        except Exception as e:
            logger.error(f"商品排序失败: {str(e)}")
            raise ProductException(f"商品排序失败: {str(e)}", e)
    
    def get_all_products(self):
        """获取所有商品元素"""
        try:
            products = self.element_ops.safe_find_elements(self.driver, *self.PRODUCTS)
            logger.debug(f"找到 {len(products)} 个商品")
            return products
        except Exception as e:
            logger.error(f"获取商品列表失败: {str(e)}")
            raise ProductException(f"获取商品列表失败: {str(e)}", e)
    
    def add_product_by_index(self, index):
        """按索引添加商品到购物车"""
        try:
            logger.info(f"添加第 {index} 个商品到购物车")
            
            products = self.get_all_products()
            if index < len(products):
                product = products[index]
                add_button = product.find_element(By.XPATH, ".//button[contains(text(),'Add to cart')]")
                self.element_ops.safe_click(self.driver, add_button)
                
                time.sleep(0.3)  # 等待添加完成
                logger.info(f"第 {index} 个商品已添加到购物车")
            else:
                raise ProductException(f"商品索引 {index} 超出范围")
                
        except Exception as e:
            logger.error(f"添加商品到购物车失败: {str(e)}")
            raise ProductException(f"添加商品到购物车失败: {str(e)}", e)
    
    def add_all_products_to_cart(self):
        """添加所有商品到购物车"""
        try:
            logger.info("开始添加所有商品到购物车")
            
            add_buttons = self.element_ops.safe_find_elements(self.driver, *self.ADD_TO_CART_BUTTON)
            for i, button in enumerate(add_buttons):
                try:
                    self.element_ops.safe_click(self.driver, button)
                    time.sleep(0.2)  # 短暂等待
                except Exception as e:
                    logger.warning(f"添加第 {i} 个商品失败: {str(e)}")
                    
            logger.info("所有商品已添加到购物车")
            
        except Exception as e:
            logger.error(f"添加所有商品失败: {str(e)}")
            raise ProductException(f"添加所有商品失败: {str(e)}", e)
    
    def get_cart_count(self):
        """获取购物车商品数量"""
        try:
            try:
                cart_badge = self.element_ops.safe_find_element(self.driver, *self.CART_BADGE, timeout=2)
                count = int(cart_badge.text)
                logger.debug(f"购物车数量: {count}")
                return count
            except:
                # 如果没有找到购物车徽章，说明购物车为空
                logger.debug("购物车为空")
                return 0
        except Exception as e:
            logger.error(f"获取购物车数量失败: {str(e)}")
            return 0
    
    def go_to_cart(self):
        """进入购物车"""
        try:
            logger.info("进入购物车")
            
            cart_link = self.element_ops.safe_find_element(self.driver, *self.CART_LINK)
            self.element_ops.safe_click(self.driver, cart_link)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("已进入购物车页面")
            
        except Exception as e:
            logger.error(f"进入购物车失败: {str(e)}")
            raise CartException(f"进入购物车失败: {str(e)}", e)
    
    def get_product_details(self, index):
        """获取商品详情"""
        try:
            products = self.get_all_products()
            if index < len(products):
                product = products[index]
                name = product.find_element(*self.PRODUCT_NAME).text
                desc = product.find_element(*self.PRODUCT_DESC).text
                price = product.find_element(*self.PRODUCT_PRICE).text
                
                product_info = {
                    "name": name,
                    "desc": desc,
                    "price": price
                }
                
                logger.debug(f"获取商品详情: {product_info}")
                return product_info
            else:
                raise ProductException(f"商品索引 {index} 超出范围")
                
        except Exception as e:
            logger.error(f"获取商品详情失败: {str(e)}")
            raise ProductException(f"获取商品详情失败: {str(e)}", e)
    
    def click_product_image(self, index):
        """点击商品图片进入详情页"""
        try:
            logger.info(f"点击第 {index} 个商品图片")
            
            image_links = self.element_ops.safe_find_elements(self.driver, *self.PRODUCT_IMAGE_LINK)
            if index < len(image_links):
                self.element_ops.safe_click(self.driver, image_links[index])
                time.sleep(0.2)  # 等待页面跳转
                logger.info(f"已进入第 {index} 个商品详情页")
            else:
                raise ProductException(f"商品图片索引 {index} 超出范围")
                
        except Exception as e:
            logger.error(f"点击商品图片失败: {str(e)}")
            raise ProductException(f"点击商品图片失败: {str(e)}", e)

# 其他页面类保持不变...
class CartPage(BasePage):
    """购物车页面"""
    
    # 页面元素定位器
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    REMOVE_BUTTON = (By.XPATH, "//button[contains(text(),'Remove')]")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    
    def get_cart_items(self):
        """获取购物车商品"""
        try:
            items = self.element_ops.safe_find_elements(self.driver, *self.CART_ITEMS)
            logger.debug(f"购物车中有 {len(items)} 个商品")
            return items
        except Exception as e:
            logger.error(f"获取购物车商品失败: {str(e)}")
            return []
    
    def remove_product_from_cart(self, index):
        """从购物车移除商品"""
        try:
            logger.info(f"从购物车移除第 {index} 个商品")
            
            remove_buttons = self.element_ops.safe_find_elements(self.driver, *self.REMOVE_BUTTON)
            if index < len(remove_buttons):
                self.element_ops.safe_click(self.driver, remove_buttons[index])
                time.sleep(0.3)  # 等待移除完成
                logger.info(f"第 {index} 个商品已从购物车移除")
            else:
                raise CartException(f"移除按钮索引 {index} 超出范围")
                
        except Exception as e:
            logger.error(f"从购物车移除商品失败: {str(e)}")
            raise CartException(f"从购物车移除商品失败: {str(e)}", e)
    
    def continue_shopping(self):
        """继续购物"""
        try:
            logger.info("点击继续购物")
            
            continue_button = self.element_ops.safe_find_element(self.driver, *self.CONTINUE_SHOPPING_BUTTON)
            self.element_ops.safe_click(self.driver, continue_button)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("已返回商品页面")
            
        except Exception as e:
            logger.error(f"继续购物失败: {str(e)}")
            raise CartException(f"继续购物失败: {str(e)}", e)
    
    def checkout(self):
        """开始结账"""
        try:
            logger.info("开始结账")
            
            checkout_button = self.element_ops.safe_find_element(self.driver, *self.CHECKOUT_BUTTON)
            self.element_ops.safe_click(self.driver, checkout_button)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("已进入结账页面")
            
        except Exception as e:
            logger.error(f"开始结账失败: {str(e)}")
            raise CheckoutException(f"开始结账失败: {str(e)}", e)

class CheckoutPage(BasePage):
    """结账页面"""
    
    # 页面元素定位器
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")
    
    def fill_checkout_info(self, first_name, last_name, postal_code):
        """填写结账信息"""
        try:
            logger.info("填写结账信息")
            
            first_name_field = self.element_ops.safe_find_element(self.driver, *self.FIRST_NAME_INPUT)
            last_name_field = self.element_ops.safe_find_element(self.driver, *self.LAST_NAME_INPUT)
            postal_code_field = self.element_ops.safe_find_element(self.driver, *self.POSTAL_CODE_INPUT)
            
            self.element_ops.safe_send_keys(first_name_field, first_name)
            self.element_ops.safe_send_keys(last_name_field, last_name)
            self.element_ops.safe_send_keys(postal_code_field, postal_code)
            
            logger.info("结账信息填写完成")
            
        except Exception as e:
            logger.error(f"填写结账信息失败: {str(e)}")
            raise CheckoutException(f"填写结账信息失败: {str(e)}", e)
    
    def continue_checkout(self):
        """继续结账"""
        try:
            logger.info("继续结账")
            
            continue_button = self.element_ops.safe_find_element(self.driver, *self.CONTINUE_BUTTON)
            self.element_ops.safe_click(self.driver, continue_button)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("已进入结账确认页面")
            
        except Exception as e:
            logger.error(f"继续结账失败: {str(e)}")
            raise CheckoutException(f"继续结账失败: {str(e)}", e)
    
    def finish_checkout(self):
        """完成结账"""
        try:
            logger.info("完成结账")
            
            finish_button = self.element_ops.safe_find_element(self.driver, *self.FINISH_BUTTON)
            self.element_ops.safe_click(self.driver, finish_button)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("结账完成")
            
        except Exception as e:
            logger.error(f"完成结账失败: {str(e)}")
            raise CheckoutException(f"完成结账失败: {str(e)}", e)
    
    def cancel_checkout(self):
        """取消结账"""
        try:
            logger.info("取消结账")
            
            cancel_button = self.element_ops.safe_find_element(self.driver, *self.CANCEL_BUTTON)
            self.element_ops.safe_click(self.driver, cancel_button)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("已取消结账")
            
        except Exception as e:
            logger.error(f"取消结账失败: {str(e)}")
            raise CheckoutException(f"取消结账失败: {str(e)}", e)

class ProductDetailPage(BasePage):
    """商品详情页面"""
    
    # 页面元素定位器
    BACK_TO_PRODUCTS_BUTTON = (By.ID, "back-to-products")
    
    def back_to_products(self):
        """返回商品列表"""
        try:
            logger.info("返回商品列表")
            
            back_button = self.element_ops.safe_find_element(self.driver, *self.BACK_TO_PRODUCTS_BUTTON)
            self.element_ops.safe_click(self.driver, back_button)
            
            time.sleep(0.2)  # 等待页面跳转
            logger.info("已返回商品列表")
            
        except Exception as e:
            logger.error(f"返回商品列表失败: {str(e)}")
            raise ProductException(f"返回商品列表失败: {str(e)}", e)