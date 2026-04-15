"""
多浏览器测试配置和工具
"""
import pytest
import yaml
from pathlib import Path
from typing import List, Dict


def get_browsers_config() -> List[Dict]:
    """获取多浏览器配置"""
    config_path = Path(__file__).parent.parent / "data" / "env_config.yaml"
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config.get("browsers", [])


def pytest_generate_tests(metafunc):
    """
    动态生成多浏览器测试参数
    
    使用方式：
    @pytest.mark.multi_browser
    def test_something(page):
        # 测试代码
        pass
    """
    # 检查是否有 multi_browser 标记
    if "multi_browser" in metafunc.fixturenames:
        browsers = get_browsers_config()
        
        # 生成参数
        metafunc.parametrize(
            "browser_name,browser_type,browser_channel",
            [
                (b["name"], b["browser_type"], b.get("browser_channel", ""))
                for b in browsers
            ],
            ids=[b["name"] for b in browsers],
            scope="session"
        )


def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line(
        "markers", 
        "multi_browser: 标记需要在多个浏览器上运行的测试"
    )
    config.addinivalue_line(
        "markers",
        "browser(name): 指定在特定浏览器上运行的测试"
    )
