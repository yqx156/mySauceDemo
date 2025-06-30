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
            
            time.sleep(0.2)  # 等待页面跳转
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
    SORT_DROPDOWN = (By.CSS_SELECTOR, "select[data-test='product-sort-container']")
    PRODUCTS = (By.CLASS_NAME, "inventory_item")
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_item_name")
    PRODUCT_DESC = (By.CLASS_NAME, "inventory_item_desc")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_item_price")
    ADD_TO_CART_BUTTON = (By.XPATH, "//button[contains(text(),'Add to cart')]")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    PRODUCT_IMAGE_LINK = (By.CSS_SELECTOR, ".inventory_item_img a")
    
    def logout(self):
        """登出功能"""
        try:
            logger.info("开始登出")
            menu_button = self.element_ops.wait_for_clickable_element(self.driver, *self.MENU_BUTTON)
            self.element_ops.safe_click(self.driver, menu_button)
            
            logout_link = self.element_ops.wait_for_clickable_element(self.driver, *self.LOGOUT_LINK)
            self.element_ops.safe_click(self.driver, logout_link)
            
            time.sleep(0.2)
            logger.info("登出完成")
            
        except Exception as e:
            logger.error(f"登出失败: {str(e)}")
            raise LoginException(f"登出失败: {str(e)}", e)
    
    def sort_products(self, sort_value="lohi"):
        """产品排序"""
        try:
            logger.info(f"开始排序产品: {sort_value}")
            dropdown_element = self.element_ops.safe_find_element(self.driver, *self.SORT_DROPDOWN)
            dropdown = Select(dropdown_element)
            dropdown.select_by_value(sort_value)
            
            # 增加等待时间，确保排序完成
            time.sleep(0.2)  # 从2秒增加到3秒
            
            # 等待页面重新加载完成
            self.element_ops.wait_for_element(self.driver, *self.PRODUCTS)
            
            logger.info("产品排序完成")
            
        except Exception as e:
            logger.error(f"产品排序失败: {str(e)}")
            raise ProductException(f"产品排序失败: {str(e)}", e)
    
    def get_all_products(self):
        """获取所有产品"""
        try:
            products = self.element_ops.safe_find_elements(self.driver, *self.PRODUCTS)
            logger.info(f"找到 {len(products)} 个产品")
            return products
        except Exception as e:
            logger.error(f"获取产品列表失败: {str(e)}")
            return []
    
    def add_product_by_index(self, idx):
        """根据索引添加产品到购物车"""
        try:
            logger.info(f"添加第 {idx} 个产品到购物车")
            items = self.get_all_products()
            if 0 <= idx < len(items):
                button = items[idx].find_element(By.TAG_NAME, "button")
                if "Add to cart" in button.text:
                    self.element_ops.safe_click(self.driver, button)
                    product_name = items[idx].find_element(*self.PRODUCT_NAME).text
                    logger.info(f"成功添加产品: {product_name}")
                    return product_name
                else:
                    logger.warning(f"产品 {idx} 已在购物车中")
                    return None
            else:
                logger.error(f"产品索引 {idx} 超出范围")
                raise ProductException(f"产品索引 {idx} 超出范围")
        except Exception as e:
            logger.error(f"添加产品失败: {str(e)}")
            raise ProductException(f"添加产品失败: {str(e)}", e)
    
    def add_all_products_to_cart(self):
        """添加所有产品到购物车"""
        try:
            logger.info("开始添加所有产品到购物车")
            items = self.get_all_products()
            added_count = 0
            
            for i, item in enumerate(items):
                try:
                    button = item.find_element(By.TAG_NAME, "button")
                    if "Add to cart" in button.text:
                        self.element_ops.safe_click(self.driver, button)
                        added_count += 1
                        time.sleep(0.3)  # 短暂延迟
                except Exception as e:
                    logger.warning(f"添加第 {i} 个产品失败: {str(e)}")
                    continue
            
            time.sleep(0.2)
            logger.info(f"成功添加 {added_count} 个产品到购物车")
            
        except Exception as e:
            logger.error(f"添加所有产品失败: {str(e)}")
            raise ProductException(f"添加所有产品失败: {str(e)}", e)
    
    def get_cart_count(self):
        """获取购物车数量"""
        try:
            badge = self.driver.find_element(*self.CART_BADGE)
            count = int(badge.text)
            logger.info(f"购物车数量: {count}")
            return count
        except:
            logger.info("购物车为空")
            return 0
    
    def go_to_cart(self):
        """进入购物车"""
        try:
            logger.info("进入购物车")
            cart_link = self.element_ops.safe_find_element(self.driver, *self.CART_LINK)
            self.element_ops.safe_click(self.driver, cart_link)
            time.sleep(0.2)
            logger.info("成功进入购物车")
            
        except Exception as e:
            logger.error(f"进入购物车失败: {str(e)}")
            raise CartException(f"进入购物车失败: {str(e)}", e)
    
    def get_product_details(self, idx):
        """获取产品详情"""
        try:
            logger.info(f"获取第 {idx} 个产品详情")
            items = self.get_all_products()
            if idx < len(items):
                item = items[idx]
                name = item.find_element(*self.PRODUCT_NAME).text
                desc = item.find_element(*self.PRODUCT_DESC).text
                price = item.find_element(*self.PRODUCT_PRICE).text
                
                product_info = {"name": name, "desc": desc, "price": price}
                logger.info(f"产品详情: {product_info}")
                return product_info
            else:
                logger.error(f"产品索引 {idx} 超出范围")
                return None
                
        except Exception as e:
            logger.error(f"获取产品详情失败: {str(e)}")
            return None
    
    def click_product_image(self, idx):
        """点击产品图片"""
        try:
            logger.info(f"点击第 {idx} 个产品图片")
            items = self.get_all_products()
            if idx < len(items):
                image_link = items[idx].find_element(*self.PRODUCT_IMAGE_LINK)
                self.element_ops.safe_click(self.driver, image_link)
                time.sleep(0.2)
                logger.info("成功进入产品详情页")
            else:
                logger.error(f"产品索引 {idx} 超出范围")
                raise ProductException(f"产品索引 {idx} 超出范围")
                
        except Exception as e:
            logger.error(f"点击产品图片失败: {str(e)}")
            raise ProductException(f"点击产品图片失败: {str(e)}", e)

class CartPage(BasePage):
    """购物车页面"""
    
    # 页面元素定位器
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    REMOVE_BUTTONS = (By.XPATH, "//button[contains(text(),'Remove')]")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    
    def remove_product_from_cart(self, idx=0):
        """从购物车移除产品"""
        try:
            logger.info(f"从购物车移除第 {idx} 个产品")
            remove_btns = self.element_ops.safe_find_elements(self.driver, *self.REMOVE_BUTTONS)
            if idx < len(remove_btns):
                self.element_ops.safe_click(self.driver, remove_btns[idx])
                time.sleep(0.2)
                logger.info("成功移除产品")
            else:
                logger.error(f"移除按钮索引 {idx} 超出范围")
                raise CartException(f"移除按钮索引 {idx} 超出范围")
                
        except Exception as e:
            logger.error(f"移除产品失败: {str(e)}")
            raise CartException(f"移除产品失败: {str(e)}", e)
    
    def continue_shopping(self):
        """继续购物"""
        try:
            logger.info("继续购物")
            continue_btn = self.element_ops.safe_find_element(self.driver, *self.CONTINUE_SHOPPING_BUTTON)
            self.element_ops.safe_click(self.driver, continue_btn)
            time.sleep(0.2)
            logger.info("返回商品页面")
            
        except Exception as e:
            logger.error(f"继续购物失败: {str(e)}")
            raise CartException(f"继续购物失败: {str(e)}", e)
    
    def checkout(self):
        """开始结账"""
        try:
            logger.info("开始结账")
            checkout_btn = self.element_ops.safe_find_element(self.driver, *self.CHECKOUT_BUTTON)
            self.element_ops.safe_click(self.driver, checkout_btn)
            time.sleep(0.2)
            logger.info("进入结账页面")
            
        except Exception as e:
            logger.error(f"开始结账失败: {str(e)}")
            raise CheckoutException(f"开始结账失败: {str(e)}", e)
    
    def get_cart_items(self):
        """获取购物车商品"""
        return self.element_ops.safe_find_elements(self.driver, *self.CART_ITEMS)

class CheckoutPage(BasePage):
    """结账页面"""
    
    # 页面元素定位器
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    CANCEL_BUTTON = (By.ID, "cancel")
    FINISH_BUTTON = (By.ID, "finish")
    
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
            
            time.sleep(0.2)
            logger.info("结账信息填写完成")
            
        except Exception as e:
            logger.error(f"填写结账信息失败: {str(e)}")
            raise CheckoutException(f"填写结账信息失败: {str(e)}", e)
    
    def continue_checkout(self):
        """继续结账"""
        try:
            logger.info("继续结账")
            continue_btn = self.element_ops.safe_find_element(self.driver, *self.CONTINUE_BUTTON)
            self.element_ops.safe_click(self.driver, continue_btn)
            time.sleep(0.2)
            logger.info("进入结账确认页面")
            
        except Exception as e:
            logger.error(f"继续结账失败: {str(e)}")
            raise CheckoutException(f"继续结账失败: {str(e)}", e)
    
    def finish_checkout(self):
        """完成结账"""
        try:
            logger.info("完成结账")
            finish_btn = self.element_ops.safe_find_element(self.driver, *self.FINISH_BUTTON)
            self.element_ops.safe_click(self.driver, finish_btn)
            time.sleep(0.2)
            logger.info("结账完成")
            
        except Exception as e:
            logger.error(f"完成结账失败: {str(e)}")
            raise CheckoutException(f"完成结账失败: {str(e)}", e)
    
    def cancel_checkout(self):
        """取消结账"""
        try:
            logger.info("取消结账")
            cancel_btn = self.element_ops.safe_find_element(self.driver, *self.CANCEL_BUTTON)
            self.element_ops.safe_click(self.driver, cancel_btn)
            time.sleep(0.2)
            logger.info("结账已取消")
            
        except Exception as e:
            logger.error(f"取消结账失败: {str(e)}")
            raise CheckoutException(f"取消结账失败: {str(e)}", e)

class ProductDetailPage(BasePage):
    """产品详情页"""
    
    # 页面元素定位器
    BACK_TO_PRODUCTS_BUTTON = (By.ID, "back-to-products")
    
    def back_to_products(self):
        """返回产品列表"""
        try:
            logger.info("返回产品列表")
            back_btn = self.element_ops.safe_find_element(self.driver, *self.BACK_TO_PRODUCTS_BUTTON)
            self.element_ops.safe_click(self.driver, back_btn)
            time.sleep(0.2)
            logger.info("成功返回产品列表")
            
        except Exception as e:
            logger.error(f"返回产品列表失败: {str(e)}")
            raise ProductException(f"返回产品列表失败: {str(e)}", e)