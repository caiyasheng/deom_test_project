"""
Pytest Fixtures
提供通用的测试夹具
"""
import pytest
from playwright.sync_api import Page
from config.config import get_config
from pages.login_page import LoginPage
from pages.main_page import MainPage, DashboardPage, UsersPage, ProfilePage, UserModal


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """
    创建登录页面对象
    
    Args:
        page: Playwright Page 对象
        
    Returns:
        LoginPage 实例
    """
    config = get_config()
    login_page = LoginPage(page)
    login_page.set_timeout(config.timeout)
    return login_page


@pytest.fixture
def logged_in_page(page: Page, login_page: LoginPage) -> MainPage:
    """
    已登录的主页面对象
    
    Args:
        page: Playwright Page 对象
        login_page: LoginPage 实例
        
    Returns:
        MainPage 实例
    """
    config = get_config()
    
    # 导航到登录页面
    login_page.navigate(config.base_url)
    
    # 使用默认账号登录
    login_page.login("admin", "admin123")
    
    # 等待登录成功
    main_page = MainPage(page)
    main_page.wait_for_element_visible('button:has-text("退出登录")', timeout=config.timeout)
    
    return main_page


@pytest.fixture
def dashboard_page(logged_in_page: MainPage) -> DashboardPage:
    """
    仪表盘页面对象
    
    Args:
        logged_in_page: 已登录的 MainPage 实例
        
    Returns:
        DashboardPage 实例
    """
    dashboard = DashboardPage(logged_in_page.page)
    dashboard.click_tab("仪表盘")
    return dashboard


@pytest.fixture
def users_page(logged_in_page: MainPage) -> UsersPage:
    """
    用户管理页面对象
    
    Args:
        logged_in_page: 已登录的 MainPage 实例
        
    Returns:
        UsersPage 实例
    """
    users = UsersPage(logged_in_page.page)
    users.click_tab("用户管理")
    return users


@pytest.fixture
def profile_page(logged_in_page: MainPage) -> ProfilePage:
    """
    个人信息页面对象
    
    Args:
        logged_in_page: 已登录的 MainPage 实例
        
    Returns:
        ProfilePage 实例
    """
    profile = ProfilePage(logged_in_page.page)
    profile.click_tab("个人信息")
    return profile


@pytest.fixture
def user_modal(page: Page) -> UserModal:
    """
    用户模态框对象
    
    Args:
        page: Playwright Page 对象
        
    Returns:
        UserModal 实例
    """
    return UserModal(page)
