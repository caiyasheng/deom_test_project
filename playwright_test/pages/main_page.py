"""
主应用页面 Page Object
包含登录后的所有功能页面
"""
from playwright.sync_api import Page, expect
from typing import List, Dict, Optional
from .base_page import BasePage


class MainPage(BasePage):
    """主应用页面类（登录后）"""
    
    def __init__(self, page: Page):
        """初始化主页面"""
        super().__init__(page)
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            expect(self.page.get_by_role("button", name="退出登录")).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False
    
    def get_welcome_text(self) -> str:
        """获取欢迎文本"""
        return self.page.get_by_text("欢迎，").text_content() or ""
    
    def logout(self) -> None:
        """退出登录"""
        self.click_by_role("button", "退出登录")
    
    def is_tab_active(self, tab_name: str) -> bool:
        """检查标签页是否激活"""
        try:
            button = self.page.get_by_role("button", name=tab_name)
            return "active" in button.get_attribute("class") or ""
        except Exception:
            return False
    
    def click_tab(self, tab_name: str) -> None:
        """点击标签页"""
        self.click_by_role("button", tab_name)
    
    def wait_for_tab_content(self, tab_name: str, timeout: int = 5000) -> None:
        """等待标签页内容加载"""
        expect(self.page.get_by_role("button", name=tab_name, selected=True)).to_be_visible(timeout=timeout)


class DashboardPage(MainPage):
    """仪表盘页面"""
    
    def __init__(self, page: Page):
        """初始化仪表盘页面"""
        super().__init__(page)
    
    def is_dashboard_visible(self) -> bool:
        """检查仪表盘是否可见"""
        return self.is_visible("h3:has-text('仪表盘')")
    
    def get_user_count(self) -> str:
        """获取用户总数"""
        try:
            stat_cards = self.page.locator(".stat-card")
            first_card = stat_cards.first
            return first_card.locator(".stat-value").text_content() or ""
        except Exception:
            return ""
    
    def get_current_user_display(self) -> str:
        """获取当前用户显示"""
        try:
            stat_cards = self.page.locator(".stat-card")
            second_card = stat_cards.nth(1)
            return second_card.locator(".stat-value").text_content() or ""
        except Exception:
            return ""


class UsersPage(MainPage):
    """用户管理页面"""
    
    def __init__(self, page: Page):
        """初始化用户管理页面"""
        super().__init__(page)
    
    def is_users_page_visible(self) -> bool:
        """检查用户管理页面是否可见"""
        return self.is_visible("h3:has-text('用户管理')")
    
    def click_add_user(self) -> None:
        """点击添加用户按钮"""
        self.click_by_role("button", "添加用户")
    
    def is_user_in_table(self, username: str) -> bool:
        """检查用户是否在表格中"""
        try:
            row = self.page.locator(f"tr:has-text('{username}')")
            return row.count() > 0
        except Exception:
            return False
    
    def get_user_row(self, username: str):
        """获取用户所在行"""
        return self.page.locator(f"tr:has-text('{username}')")
    
    def click_edit_button(self, username: str) -> None:
        """点击编辑按钮"""
        row = self.get_user_row(username)
        row.get_by_role("button", name="编辑").click()
    
    def click_delete_button(self, username: str) -> None:
        """点击删除按钮"""
        row = self.get_user_row(username)
        row.get_by_role("button", name="删除").click()
    
    def get_table_rows_count(self) -> int:
        """获取表格行数"""
        try:
            rows = self.page.locator("tbody tr")
            return rows.count()
        except Exception:
            return 0


class ProfilePage(MainPage):
    """个人信息页面"""
    
    def __init__(self, page: Page):
        """初始化个人信息页面"""
        super().__init__(page)
    
    def is_profile_visible(self) -> bool:
        """检查个人信息页面是否可见"""
        return self.is_visible("h3:has-text('个人信息')")
    
    def get_user_info(self) -> Dict[str, str]:
        """获取用户信息"""
        try:
            info = {}
            info_items = self.page.locator(".info-item")
            count = info_items.count()
            
            for i in range(count):
                item = info_items.nth(i)
                label = item.locator("label").text_content() or ""
                value = item.locator("span").text_content() or ""
                
                if "用户 ID" in label:
                    info["id"] = value
                elif "用户名" in label:
                    info["username"] = value
                elif "邮箱" in label:
                    info["email"] = value
            
            return info
        except Exception:
            return {}


class UserModal(BasePage):
    """添加/编辑用户模态框"""
    
    def __init__(self, page: Page):
        """初始化模态框"""
        super().__init__(page)
    
    def is_visible(self) -> bool:
        """检查模态框是否可见"""
        return super().is_visible(".modal-content")
    
    def get_modal_title(self) -> str:
        """获取模态框标题"""
        try:
            return self.page.locator(".modal-header h3").text_content() or ""
        except Exception:
            return ""
    
    def enter_username(self, username: str) -> None:
        """输入用户名"""
        self.fill_by_role("textbox", "用户名", username)
    
    def enter_email(self, email: str) -> None:
        """输入邮箱"""
        self.fill_by_role("textbox", "邮箱", email)
    
    def enter_password(self, password: str) -> None:
        """输入密码"""
        self.fill_by_role("textbox", "密码", password)
    
    def click_save(self) -> None:
        """点击保存按钮"""
        self.click_by_role("button", "保存")
    
    def click_cancel(self) -> None:
        """点击取消按钮"""
        self.click_by_role("button", "取消")
    
    def click_close(self) -> None:
        """点击关闭按钮"""
        self.click_by_role("button", "×")
    
    def add_user(self, username: str, email: str, password: str) -> None:
        """
        添加用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
        """
        self.enter_username(username)
        self.enter_email(email)
        self.enter_password(password)
        self.click_save()
    
    def edit_user(self, email: str = None, password: str = None) -> None:
        """
        编辑用户
        
        Args:
            email: 新邮箱（可选）
            password: 新密码（可选）
        """
        if email:
            self.enter_email(email)
        if password:
            self.enter_password(password)
        self.click_save()
    
    def is_closed(self) -> bool:
        """检查模态框是否已关闭"""
        return not self.is_visible(".modal-content")
