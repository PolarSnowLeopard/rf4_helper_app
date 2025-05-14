"""配置加载工具"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器
    
    用于加载和保存应用程序配置
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        """初始化配置"""
        self.config = {}
        self.config_dir = os.environ.get('RF4_CONFIG_DIR', 
                           str(Path.home() / '.rf4_helper'))
        self.config_file = os.environ.get('RF4_CONFIG_FILE', 
                           os.path.join(self.config_dir, 'config.json'))
        
        # 创建配置目录（如果不存在）
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
                logger.info(f"创建配置目录: {self.config_dir}")
            except Exception as e:
                logger.error(f"创建配置目录失败: {e}")
        
        # 加载配置
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        # 先尝试加载用户配置
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    logger.info(f"从 {self.config_file} 加载配置成功")
                    return self.config
        except Exception as e:
            logger.error(f"加载用户配置失败: {e}")
        
        # 如果用户配置不存在或加载失败，加载默认配置
        try:
            default_config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'default_config.json'
            )
            if os.path.exists(default_config_path):
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    logger.info(f"从 {default_config_path} 加载默认配置成功")
            else:
                logger.warning(f"默认配置文件不存在: {default_config_path}")
                # 使用硬编码的默认配置
                self.config = {
                    "api_base_url": "http://localhost:5000/api",
                    "debug": False,
                    "language": "zh_CN"
                }
        except Exception as e:
            logger.error(f"加载默认配置失败: {e}")
            # 使用硬编码的默认配置
            self.config = {
                "api_base_url": "http://localhost:5000/api",
                "debug": False,
                "language": "zh_CN"
            }
        
        return self.config
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            logger.info(f"配置保存到 {self.config_file} 成功")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """更新多个配置项"""
        self.config.update(config_dict)
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

# 创建全局配置加载器实例，方便导入使用
config_loader = ConfigLoader() 