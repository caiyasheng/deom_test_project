"""
配置管理模块
支持多环境配置切换
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """配置管理类"""
    
    def __init__(self, env: str = "test"):
        """
        初始化配置
        
        Args:
            env: 环境名称 (test, env)
        """
        self.env = env
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载环境配置文件"""
        config_path = Path(__file__).parent.parent / "data" / "env_config.yaml"
        
        with open(config_path, "r", encoding="utf-8") as f:
            all_configs = yaml.safe_load(f)
        
        if self.env not in all_configs:
            raise ValueError(f"未知的环境：{self.env}，可用环境：{list(all_configs.keys())}")
        
        return all_configs[self.env]
    
    @property
    def base_url(self) -> str:
        """获取基础 URL"""
        return self.config_data.get("base_url", "http://localhost:11011")
    
    @property
    def timeout(self) -> int:
        """获取超时时间（毫秒）"""
        return self.config_data.get("timeout", 30000)
    
    @property
    def headless(self) -> bool:
        """是否无头模式"""
        return self.config_data.get("headless", False)
    
    @property
    def browser_type(self) -> str:
        """浏览器类型 (chromium, webkit)"""
        return self.config_data.get("browser_type", "chromium")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config_data.get(key, default)


# 全局配置实例（将在 conftest.py 中根据命令行参数初始化）
_config: Config = None


def get_config() -> Config:
    """获取全局配置实例"""
    if _config is None:
        raise RuntimeError("配置未初始化，请在 conftest.py 中先初始化配置")
    return _config


def init_config(env: str = "test") -> None:
    """初始化全局配置"""
    global _config
    _config = Config(env)
