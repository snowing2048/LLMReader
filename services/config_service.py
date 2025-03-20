# services/config_service.py
import json
from pathlib import Path
from typing import Dict, Any, List
from core.logger import logger

class ConfigService:
    _instance = None
    _config_file = Path('config')
    _default_config = {
        'api_key': '',
        'api_url': '',
        'last_library_path': '',
        'last_folder_path': '',
        'window': {
            'width': 1200,
            'height': 800,
            'x': 100,
            'y': 100
        },
        'splitter_sizes': [200, 400, 400, 200],
        'image_viewer_splitter_sizes': [700, 300],
        'zoom_level': 1.0,
        'categories': {}
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # 避免重复初始化
        if getattr(self, '_initialized', False):
            return
            
        self._config = self._load_config()
        self._initialized = True
        logger.info("配置服务初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """从配置文件加载配置，如果文件不存在则创建默认配置"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("成功加载配置文件")
                    return config
            logger.info("配置文件不存在，使用默认配置")
            return self._default_config.copy()
        except Exception as e:
            logger.error(f'加载配置文件失败: {e}')
            return self._default_config.copy()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info("成功保存配置文件")
        except Exception as e:
            logger.error(f'保存配置文件失败: {e}')
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项的值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项的值并保存"""
        self._config[key] = value
        self.save_config()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置项"""
        self._config.update(config_dict)
        self.save_config()
    
    @property
    def api_key(self) -> str:
        return self.get('api_key', '')
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        self.set('api_key', value)
    
    @property
    def api_url(self) -> str:
        return self.get('api_url', '')
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        self.set('api_url', value)
    
    @property
    def last_library_path(self) -> str:
        return self.get('last_library_path', '')
    
    @last_library_path.setter
    def last_library_path(self, value: str) -> None:
        self.set('last_library_path', value)
    
    @property
    def last_folder_path(self) -> str:
        return self.get('last_folder_path', '')
    
    @last_folder_path.setter
    def last_folder_path(self, value: str) -> None:
        self.set('last_folder_path', value)
    
    @property
    def window_geometry(self) -> Dict[str, int]:
        return self.get('window', {})
    
    @window_geometry.setter
    def window_geometry(self, value: Dict[str, int]) -> None:
        self.set('window', value)
    
    @property
    def splitter_sizes(self) -> List[int]:
        return self.get('splitter_sizes', [200, 400, 400, 200])
    
    @splitter_sizes.setter
    def splitter_sizes(self, value: List[int]) -> None:
        self.set('splitter_sizes', value)
    
    @property
    def image_viewer_splitter_sizes(self) -> List[int]:
        return self.get('image_viewer_splitter_sizes', [700, 300])
    
    @image_viewer_splitter_sizes.setter
    def image_viewer_splitter_sizes(self, value: List[int]) -> None:
        self.set('image_viewer_splitter_sizes', value)
    
    @property
    def zoom_level(self) -> float:
        return self.get('zoom_level', 1.0)
    
    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        self.set('zoom_level', value)
    
    @property
    def categories(self) -> Dict[str, Any]:
        return self.get('categories', {})
    
    @categories.setter
    def categories(self, value: Dict[str, Any]) -> None:
        self.set('categories', value)