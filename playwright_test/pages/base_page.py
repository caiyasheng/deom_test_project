"""
基础 Page Object 类
所有 Page Object 的基类
"""
from playwright.sync_api import Page, expect
from typing import Optional
import time


class BasePage:
    """Page Object 基类"""
    
    def __init__(self, page: Page):
        """
        初始化基础页面
        
        Args:
            page: Playwright Page 对象
        """
        self.page = page
        self.timeout = 30000
    
    def set_timeout(self, timeout: int) -> None:
        """设置超时时间"""
        self.timeout = timeout
        self.page.set_default_timeout(timeout)
    
    def navigate(self, url: str) -> None:
        """导航到指定 URL"""
        self.page.goto(url)
    
    def get_by_role_safe(self, role: str, name: str = None, **kwargs):
        """
        使用 get_by_role 定位元素（优先使用）
        
        Args:
            role: 角色类型 (button, link, textbox, etc.)
            name: 元素的无障碍名称
            **kwargs: 其他选项
            
        Returns:
            Locator 对象
        """
        if name:
            return self.page.get_by_role(role, name=name, **kwargs)
        return self.page.get_by_role(role, **kwargs)
    
    def click_by_role(self, role: str, name: str, timeout: Optional[int] = None) -> None:
        """
        点击通过 role 定位的元素
        
        Args:
            role: 角色类型
            name: 元素名称
            timeout: 超时时间（可选）
        """
        element = self.get_by_role_safe(role, name)
        if timeout:
            element.click(timeout=timeout)
        else:
            element.click()
    
    def fill_by_role(self, role: str, name: str, value: str) -> None:
        """
        填充输入框
        
        Args:
            role: 角色类型（通常是 textbox）
            name: 元素名称
            value: 要填充的值
        """
        element = self.get_by_role_safe(role, name=name)
        element.fill(value)
    
    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        try:
            expect(self.page.locator(selector)).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False
    
    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可用"""
        try:
            expect(self.page.locator(selector)).to_be_enabled(timeout=5000)
            return True
        except Exception:
            return False
    
    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """等待元素出现"""
        if timeout:
            self.page.wait_for_selector(selector, timeout=timeout)
        else:
            self.page.wait_for_selector(selector)
    
    def wait_for_element_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        """等待元素可见"""
        if timeout:
            expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
        else:
            expect(self.page.locator(selector)).to_be_visible()
    
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        return self.page.locator(selector).text_content()
    
    def get_text_by_role(self, role: str, name: str) -> str:
        """通过 role 获取元素文本"""
        return self.get_by_role_safe(role, name).text_content()
    
    def screenshot(self, name: str) -> None:
        """截图"""
        self.page.screenshot(path=f"screenshots/{name}.png")
    
    def wait(self, seconds: float) -> None:
        """强制等待（仅在必要时使用）"""
        time.sleep(seconds)
