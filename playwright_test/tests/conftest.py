"""
Pytest 配置文件
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config.config import Config, init_config
from fixtures.fixtures import (
    login_page,
    logged_in_page,
    dashboard_page,
    users_page,
    profile_page,
    user_modal,
)


@pytest.fixture(scope="session")
def browser_type(request):
    """获取浏览器类型（从命令行参数）"""
    return request.config.getoption("--browser-type")


@pytest.fixture(scope="session")
def browser_channel(request):
    """获取浏览器通道（从命令行参数）"""
    return request.config.getoption("--browser-channel")


@pytest.fixture(scope="session")
def browser_name(browser_type: str, browser_channel: str):
    """
    获取浏览器名称（用于测试报告）
    
    Args:
        browser_type: 浏览器类型
        browser_channel: 浏览器通道
        
    Returns:
        浏览器名称字符串
    """
    if browser_channel:
        return browser_channel
    return browser_type


@pytest.fixture(scope="session")
def playwright():
    """创建 Playwright 实例"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: sync_playwright, browser_type: str, browser_channel: str, request):
    """
    创建浏览器实例
    
    Args:
        playwright: Playwright 实例
        browser_type: 浏览器类型 (chromium, webkit)
        browser_channel: 浏览器通道 (chrome, chromium, etc.)
        
    Returns:
        Browser 实例
    """
    # 获取配置
    env = request.config.getoption("--env")
    config = Config(env)
    
    # 浏览器启动参数
    launch_args = {
        "headless": config.headless,
    }
    
    # 添加额外的启动参数避免白屏闪烁
    if config.headless:
        launch_args["args"] = [
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor"
        ]
    
    # 如果是 Chromium 且指定了 channel
    if browser_type == "chromium" and browser_channel:
        launch_args["channel"] = browser_channel
    
    # 启动浏览器
    if browser_type == "webkit":
        browser = playwright.webkit.launch(**launch_args)
    else:
        if browser_channel:
            browser = playwright.chromium.launch(**launch_args)
        else:
            browser = playwright.chromium.launch(**launch_args)
    
    yield browser
    
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser, request):
    """
    创建浏览器上下文
    
    Args:
        browser: Browser 实例
        
    Returns:
        BrowserContext 实例
    """
    # 获取配置
    env = request.config.getoption("--env")
    config = Config(env)
    
    # 创建上下文
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        base_url=config.base_url,
    )
    
    yield context
    
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """
    创建页面
    
    Args:
        context: BrowserContext 实例
        
    Returns:
        Page 实例
    """
    page = context.new_page()
    page.set_default_timeout(config.timeout if (config := getattr(context, "_config", None)) else 30000)
    yield page


def pytest_addoption(parser):
    """添加自定义命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="测试环境 (test, env)"
    )
    parser.addoption(
        "--browser-type",
        action="store",
        default="chromium",
        help="浏览器类型 (chromium, webkit)"
    )
    parser.addoption(
        "--browser-channel",
        action="store",
        default=None,
        help="浏览器通道 (chrome, chromium, etc.)"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_config(request):
    """
    初始化配置（自动执行）
    
    Args:
        request: Pytest request 对象
    """
    env = request.config.getoption("--env")
    init_config(env)
