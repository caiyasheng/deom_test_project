"""
登录功能测试用例
使用数据驱动方式测试登录功能
"""
import pytest
import allure
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from utils.helpers import get_login_test_data, generate_test_id


@allure.feature("登录功能")
class TestLogin:
    """登录功能测试类"""
    
    @allure.story("成功登录")
    @pytest.mark.parametrize(
        "username,password,description",
        [
            (account["username"], account["password"], account["description"])
            for account in get_login_test_data().get("valid_accounts", [])
        ],
        ids=[
            generate_test_id("valid", account["username"])
            for account in get_login_test_data().get("valid_accounts", [])
        ]
    )
    @allure.title("成功登录测试 - {description}")
    def test_login_success(self, page: Page, login_page: LoginPage, 
                          username: str, password: str, description: str):
        """
        测试成功登录
        
        Args:
            page: Playwright Page 对象
            login_page: LoginPage 实例
            username: 用户名
            password: 密码
            description: 测试描述
        """
        # 导航到登录页面
        login_page.navigate()
        
        # 执行登录
        login_page.login(username, password)
        
        # 验证登录成功（检查退出登录按钮是否出现）
        expect(page.get_by_role("button", name="退出登录")).to_be_visible(timeout=30000)
        
        # 验证欢迎信息显示正确
        welcome_text = page.get_by_text("欢迎，").text_content()
        assert username in welcome_text, f"欢迎信息应该包含用户名：{username}"
    
    @allure.story("失败登录")
    @pytest.mark.parametrize(
        "username,password,expected_error,description",
        [
            (
                account["username"], 
                account["password"], 
                account.get("expected_error", ""),
                account["description"]
            )
            for account in get_login_test_data().get("invalid_accounts", [])
        ],
        ids=[
            generate_test_id("invalid", account["description"])
            for account in get_login_test_data().get("invalid_accounts", [])
        ]
    )
    @allure.title("失败登录测试 - {description}")
    def test_login_failure(self, page: Page, login_page: LoginPage,
                          username: str, password: str, 
                          expected_error: str, description: str):
        """
        测试失败登录
        
        Args:
            page: Playwright Page 对象
            login_page: LoginPage 实例
            username: 用户名
            password: 密码
            expected_error: 预期错误消息
            description: 测试描述
        """
        # 导航到登录页面
        login_page.navigate()
        
        # 执行登录
        login_page.login(username, password)
        
        # 验证仍然在登录页面（没有跳转）
        assert login_page.is_login_form_visible(), "登录失败后应该仍在登录页面"
        
        # 如果有预期错误消息，验证错误消息显示
        if expected_error:
            error_msg = login_page.get_error_message()
            assert error_msg, "应该显示错误消息"
    
    @allure.story("登录页面验证")
    @allure.title("验证登录页面元素显示")
    def test_login_page_elements(self, page: Page, login_page: LoginPage):
        """
        测试登录页面元素显示
        
        Args:
            page: Playwright Page 对象
            login_page: LoginPage 实例
        """
        # 导航到登录页面
        login_page.navigate()
        
        # 验证页面标题
        expect(page).to_have_title("用户管理系统")
        
        # 验证登录表单存在
        assert login_page.is_login_form_visible(), "登录表单应该可见"
        
        # 验证演示账号信息显示
        demo_info = login_page.get_demo_info()
        assert "admin" in demo_info, "应该显示 admin 账号信息"
        assert "test" in demo_info, "应该显示 test 账号信息"
