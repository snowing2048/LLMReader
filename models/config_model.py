# models/config_model.py
from typing import Dict, Any, List
from services.config_service import ConfigService

class ConfigModel:
    def __init__(self, config_service=None):
        self.config_service = config_service or ConfigService()
    
    @property
    def api_key(self) -> str:
        return self.config_service.get('api_key', '')
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        self.config_service.set('api_key', value)
    
    @property
    def api_url(self) -> str:
        return self.config_service.get('api_url', '')
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        self.config_service.set('api_url', value)
    
    @property
    def last_library_path(self) -> str:
        return self.config_service.get('last_library_path', '')
    
    @last_library_path.setter
    def last_library_path(self, value: str) -> None:
        self.config_service.set('last_library_path', value)
    
    @property
    def window_geometry(self) -> Dict[str, int]:
        return self.config_service.get('window', {})
    
    @window_geometry.setter
    def window_geometry(self, value: Dict[str, int]) -> None:
        self.config_service.set('window', value)
    
    @property
    def splitter_sizes(self) -> List[int]:
        return self.config_service.get('splitter_sizes', [200, 400, 400, 200])
    
    @splitter_sizes.setter
    def splitter_sizes(self, value: List[int]) -> None:
        self.config_service.set('splitter_sizes', value)
    
    @property
    def image_viewer_splitter_sizes(self) -> List[int]:
        return self.config_service.get('image_viewer_splitter_sizes', [700, 300])
    
    @image_viewer_splitter_sizes.setter
    def image_viewer_splitter_sizes(self, value: List[int]) -> None:
        self.config_service.set('image_viewer_splitter_sizes', value)
    
    @property
    def zoom_level(self) -> float:
        return self.config_service.get('zoom_level', 1.0)
    
    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        self.config_service.set('zoom_level', value)
    
    @property
    def categories(self) -> Dict[str, Any]:
        return self.config_service.get('categories', {})
    
    @categories.setter
    def categories(self, value: Dict[str, Any]) -> None:
        self.config_service.set('categories', value)