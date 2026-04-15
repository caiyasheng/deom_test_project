"""
登录页面 Page Object
"""
from playwright.sync_api import Page
from .base_page import BasePage


class LoginPage(BasePage):
    """登录页面类"""
    
    # 页面元素定位（使用 get_by_role 优先策略）
    USERNAME_INPUT = "textbox"
    PASSWORD_INPUT = "textbox"
    LOGIN_BUTTON = "button"
    ERROR_MESSAGE = ".error-msg"
    DEMO_INFO = ".demo-info"
    
    def __init__(self, page: Page):
        """初始化登录页面"""
        super().__init__(page)
    
    def navigate(self, url: str = None) -> None:
        """导航到登录页面"""
        if url:
            super().navigate(url)
        else:
            # 从配置获取 base_url
            from config.config import get_config
            config = get_config()
            super().navigate(config.base_url)
    
    def enter_username(self, username: str) -> None:
        """
        输入用户名
        
        Args:
            username: 用户名
        """
        # 使用 placeholder 定位（因为 input 没有 aria-label）
        self.page.get_by_placeholder("请输入用户名").fill(username)
    
    def enter_password(self, password: str) -> None:
        """
        输入密码
        
        Args:
            password: 密码
        """
        # 使用 placeholder 定位
        self.page.get_by_placeholder("请输入密码").fill(password)
    
    def click_login(self) -> None:
        """点击登录按钮"""
        self.page.get_by_role("button", name="登录").click()
    
    def login(self, username: str, password: str) -> None:
        """
        执行登录操作
        
        Args:
            username: 用户名
            password: 密码
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
    
    def get_error_message(self) -> str:
        """获取错误消息"""
        try:
            return self.page.locator(self.ERROR_MESSAGE).text_content() or ""
        except Exception:
            return ""
    
    def is_error_message_visible(self) -> bool:
        """检查错误消息是否可见"""
        return self.is_visible(self.ERROR_MESSAGE)
    
    def get_demo_info(self) -> str:
        """获取演示账号信息"""
        try:
            return self.page.locator(self.DEMO_INFO).text_content() or ""
        except Exception:
            return ""
    
    def is_login_form_visible(self) -> bool:
        """检查登录表单是否可见"""
        return (
            self.is_visible('input[type="text"]') and
            self.is_visible('input[type="password"]') and
            self.is_visible('button:has-text("登录")')
        )
