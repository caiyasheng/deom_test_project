"""
导航功能测试用例
测试标签页切换功能
"""
import pytest
import allure
from playwright.sync_api import Page, expect
from pages.main_page import MainPage, DashboardPage, UsersPage, ProfilePage
from utils.helpers import get_navigation_test_data, generate_test_id


@allure.feature("导航功能")
class TestNavigation:
    """导航功能测试类"""
    
    @allure.story("标签页切换")
    @pytest.mark.parametrize(
        "tab_id,tab_name,expected_title",
        [
            (
                tab["tab_id"],
                tab["tab_name"],
                tab["expected_title"]
            )
            for tab in get_navigation_test_data().get("tabs", [])
        ],
        ids=[
            generate_test_id("tab", tab["tab_id"])
            for tab in get_navigation_test_data().get("tabs", [])
        ]
    )
    @allure.title("标签页切换测试 - {tab_name}")
    def test_switch_tabs(self, page: Page, logged_in_page: MainPage,
                        tab_id: str, tab_name: str, expected_title: str):
        """
        测试标签页切换功能
        
        Args:
            page: Playwright Page 对象
            logged_in_page: MainPage 实例
            tab_id: 标签页 ID
            tab_name: 标签页名称
            expected_title: 预期标题
        """
        # 点击标签页
        logged_in_page.click_tab(tab_name)
        
        # 验证标签页激活状态
        assert logged_in_page.is_tab_active(tab_name), f"标签页 {tab_name} 应该被激活"
        
        # 验证内容区域显示正确
        if tab_id == "dashboard":
            dashboard = DashboardPage(page)
            assert dashboard.is_dashboard_visible(), "仪表盘内容应该可见"
        elif tab_id == "users":
            users = UsersPage(page)
            assert users.is_users_page_visible(), "用户管理内容应该可见"
        elif tab_id == "profile":
            profile = ProfilePage(page)
            assert profile.is_profile_visible(), "个人信息内容应该可见"
    
    @allure.story("退出登录")
    @allure.title("测试退出登录功能")
    def test_logout(self, page: Page, logged_in_page: MainPage):
        """
        测试退出登录功能
        
        Args:
            page: Playwright Page 对象
            logged_in_page: MainPage 实例
        """
        # 验证已登录状态
        assert logged_in_page.is_logged_in(), "应该处于登录状态"
        
        # 退出登录
        logged_in_page.logout()
        
        # 等待页面跳转到登录页
        page.wait_for_timeout(2000)
        
        # 验证已退出登录（检查登录表单是否显示）
        from pages.login_page import LoginPage
        login_page = LoginPage(page)
        assert login_page.is_login_form_visible(), "退出登录后应该显示登录表单"
