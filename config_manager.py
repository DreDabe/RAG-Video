import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot


class ConfigManager(QObject):
    configChanged = Signal()

    def __init__(self, data_dir=None):
        super().__init__()
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.config_file = self.data_dir / "config.json"
        self.config = {
            'dify': {
                'dataset_api': 'dataset-nCFE6gRoqoLnb5Vdn3O3vPc0',
                'dataset_id': '440bcad8-f7b1-4804-bae3-2ff47e268fee',
                'app_url': 'http://localhost/v1/chat-messages',
                'app_api': 'app-V2QqKcBG5msVqGCxPIgm2fR3'
            },
            'general': {
                'language': '简体中文'
            }
        }
        
        self.load_config()

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _merge_config(self, loaded_config):
        for section in self.config:
            if section in loaded_config:
                for key in self.config[section]:
                    if key in loaded_config[section]:
                        self.config[section][key] = loaded_config[section][key]

    @Slot(str, str, str)
    def set_dify_config(self, key, value):
        if 'dify' not in self.config:
            self.config['dify'] = {}
        self.config['dify'][key] = value
        self.save_config()
        self.configChanged.emit()

    @Slot(str, str)
    def set_general_config(self, key, value):
        if 'general' not in self.config:
            self.config['general'] = {}
        self.config['general'][key] = value
        self.save_config()
        self.configChanged.emit()

    @Slot(str, result=str)
    def get_dify_config(self, key):
        return self.config.get('dify', {}).get(key, '')

    @Slot(str, result=str)
    def get_general_config(self, key):
        return self.config.get('general', {}).get(key, '')

    @Slot(result=str)
    def get_dataset_api(self):
        return self.config.get('dify', {}).get('dataset_api', '')

    @Slot(result=str)
    def get_dataset_id(self):
        return self.config.get('dify', {}).get('dataset_id', '')

    @Slot(result=str)
    def get_app_url(self):
        return self.config.get('dify', {}).get('app_url', '')

    @Slot(result=str)
    def get_app_api(self):
        return self.config.get('dify', {}).get('app_api', '')

    @Slot(result=str)
    def get_language(self):
        return self.config.get('general', {}).get('language', '简体中文')

    @Slot(str)
    def set_dataset_api(self, value):
        self.set_dify_config('dataset_api', value)

    @Slot(str)
    def set_dataset_id(self, value):
        self.set_dify_config('dataset_id', value)

    @Slot(str)
    def set_app_url(self, value):
        self.set_dify_config('app_url', value)

    @Slot(str)
    def set_app_api(self, value):
        self.set_dify_config('app_api', value)

    @Slot(str)
    def set_language(self, value):
        self.set_general_config('language', value)
