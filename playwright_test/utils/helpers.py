"""
工具函数模块
"""
import yaml
from pathlib import Path
from typing import Any, Dict, List


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    加载 YAML 文件
    
    Args:
        file_path: YAML 文件路径
        
    Returns:
        加载的数据字典
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_test_data() -> Dict[str, Any]:
    """
    获取测试数据
    
    Returns:
        测试数据字典
    """
    data_path = Path(__file__).parent.parent / "data" / "test_data.yaml"
    return load_yaml_file(data_path)


def get_login_test_data() -> Dict[str, List[Dict[str, str]]]:
    """
    获取登录测试数据
    
    Returns:
        登录测试数据（包含有效和无效账号）
    """
    test_data = get_test_data()
    return test_data.get("login", {})


def get_user_management_test_data() -> Dict[str, Any]:
    """
    获取用户管理测试数据
    
    Returns:
        用户管理测试数据
    """
    test_data = get_test_data()
    return test_data.get("user_management", {})


def get_navigation_test_data() -> Dict[str, Any]:
    """
    获取导航测试数据
    
    Returns:
        导航测试数据
    """
    test_data = get_test_data()
    return test_data.get("navigation", {})


def generate_test_id(prefix: str, *args) -> str:
    """
    生成测试用例 ID
    
    Args:
        prefix: 前缀
        *args: 用于生成 ID 的参数
        
    Returns:
        生成的测试 ID
    """
    return f"{prefix}_{'_'.join(str(arg) for arg in args)}"
