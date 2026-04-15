"""
Pages 模块初始化
"""
from .base_page import BasePage
from .login_page import LoginPage
from .main_page import MainPage, DashboardPage, UsersPage, ProfilePage, UserModal

__all__ = [
    "BasePage",
    "LoginPage",
    "MainPage",
    "DashboardPage",
    "UsersPage",
    "ProfilePage",
    "UserModal",
]
