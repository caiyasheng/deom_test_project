"""
简单的冒烟测试 - 验证基本功能
"""
import pytest
import allure
from playwright.sync_api import Page, expect
from config.config import get_config


@allure.feature("冒烟测试")
class TestSmoke:
    """冒烟测试类 - 验证最基本的功能"""
    
    @allure.story("页面加载")
    @allure.title("验证首页可以正常加载")
    def test_homepage_load(self, page: Page):
        """
        测试首页加载
        
        Args:
            page: Playwright Page 对象
        """
        config = get_config()
        
        # 导航到首页
        page.goto(config.base_url)
        
        # 等待页面加载
        expect(page).to_have_title("用户管理系统", timeout=30000)
        
        # 验证登录表单存在
        assert page.get_by_placeholder("请输入用户名").is_visible()
        assert page.get_by_placeholder("请输入密码").is_visible()
        assert page.get_by_role("button", name="登录").is_visible()
    
    @allure.story("登录功能")
    @allure.title("验证可以成功登录")
    def test_login_success(self, page: Page):
        """
        测试成功登录
        
        Args:
            page: Playwright Page 对象
        """
        config = get_config()
        
        # 导航到首页
        page.goto(config.base_url)
        
        # 执行登录
        page.get_by_placeholder("请输入用户名").fill("admin")
        page.get_by_placeholder("请输入密码").fill("admin123")
        page.get_by_role("button", name="登录").click()
        
        # 等待登录成功
        expect(page.get_by_role("button", name="退出登录")).to_be_visible(timeout=30000)
        
        # 验证欢迎信息显示（只要有"欢迎，"就说明登录成功了）
        welcome_text = page.get_by_text("欢迎，").text_content()
        assert "欢迎，" in welcome_text or len(welcome_text) > 0
