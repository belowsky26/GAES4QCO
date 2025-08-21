# quantum_opt_framework/config/settings.py
import yaml
from pathlib import Path

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_path = Path(__file__).parent / "default.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, key, default=None):
        return self.config.get(key, default)