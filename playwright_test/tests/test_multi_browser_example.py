"""
多浏览器兼容性测试示例
演示如何编写一次，在多个浏览器上运行
"""
import pytest
import allure
from playwright.sync_api import Page, expect


@allure.feature("多浏览器兼容性测试")
class TestMultiBrowser:
    """多浏览器兼容性测试类"""
    
    @pytest.mark.multi_browser
    @allure.story("基础页面加载")
    @allure.title("多浏览器 - 页面加载测试 [{browser_name}]")
    def test_page_load(self, page: Page, browser_name: str):
        """
        测试页面在不同浏览器上的加载
        
        Args:
            page: Playwright Page 对象
            browser_name: 浏览器名称（由 multi_browser fixture 提供）
        """
        # 导航到页面
        page.goto("/")
        
        # 验证页面标题
        expect(page).to_have_title("用户管理系统")
        
        # 验证登录表单存在
        assert page.get_by_role("textbox", name="用户名").is_visible()
        assert page.get_by_role("textbox", name="密码").is_visible()
        assert page.get_by_role("button", name="登录").is_visible()
    
    @pytest.mark.multi_browser
    @allure.story("登录功能")
    @allure.title("多浏览器 - 登录测试 [{browser_name}]")
    def test_login(self, page: Page, browser_name: str):
        """
        测试登录功能在不同浏览器上的表现
        
        Args:
            page: Playwright Page 对象
            browser_name: 浏览器名称
        """
        # 导航到登录页面
        page.goto("/")
        
        # 执行登录
        page.get_by_role("textbox", name="用户名").fill("admin")
        page.get_by_role("textbox", name="密码").fill("admin123")
        page.get_by_role("button", name="登录").click()
        
        # 验证登录成功
        expect(page.get_by_role("button", name="退出登录")).to_be_visible(timeout=30000)
        
        # 验证欢迎信息
        welcome_text = page.get_by_text("欢迎，").text_content()
        assert "admin" in welcome_text


# 单独指定浏览器的测试示例
@pytest.mark.browser("chrome")
@allure.feature("Chrome 浏览器特定测试")
def test_chrome_specific(page: Page):
    """只在 Chrome 浏览器上运行的测试"""
    page.goto("/")
    assert page.title() == "用户管理系统"


@pytest.mark.browser("webkit")
@allure.feature("WebKit 浏览器特定测试")
def test_webkit_specific(page: Page):
    """只在 WebKit 浏览器上运行的测试"""
    page.goto("/")
    assert page.title() == "用户管理系统"
