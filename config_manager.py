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
            },
            'knowledge_update': {
                'platform': 'Bilibili',
                'type': '收藏夹',
                'url': 'https://www.bilibili.com/medialist/play/ml387412427',
                'cookie': '',
                'whisper_path': 'utils/whisper',
                'ollama_url': 'http://localhost:11434/api/generate',
                'ollama_model': 'deepseek-r1:8b'
            },
            'model': {
                'provider': 'ollama',
                'custom_models': {
                    'ollama': [],
                    'openai': [],
                    'anthropic': [],
                    'qwen': [],
                    'deepseek': []
                },
                'active_model': ''
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

    @Slot(result=str)
    def get_knowledge_platform(self):
        return self.config.get('knowledge_update', {}).get('platform', 'Bilibili')

    @Slot(result=str)
    def get_knowledge_type(self):
        return self.config.get('knowledge_update', {}).get('type', '收藏夹')

    @Slot(result=str)
    def get_knowledge_url(self):
        return self.config.get('knowledge_update', {}).get('url', '')

    @Slot(result=str)
    def get_knowledge_cookie(self):
        return self.config.get('knowledge_update', {}).get('cookie', '')

    @Slot(result=str)
    def get_whisper_path(self):
        return self.config.get('knowledge_update', {}).get('whisper_path', 'utils/whisper')

    @Slot(result=str)
    def get_ollama_url(self):
        return self.config.get('knowledge_update', {}).get('ollama_url', 'http://localhost:11434/api/generate')

    @Slot(result=str)
    def get_ollama_model(self):
        return self.config.get('knowledge_update', {}).get('ollama_model', 'deepseek-r1:8b')

    @Slot(str)
    def set_knowledge_platform(self, value):
        self._set_knowledge_config('platform', value)

    @Slot(str)
    def set_knowledge_type(self, value):
        self._set_knowledge_config('type', value)

    @Slot(str)
    def set_knowledge_url(self, value):
        self._set_knowledge_config('url', value)

    @Slot(str)
    def set_knowledge_cookie(self, value):
        self._set_knowledge_config('cookie', value)

    @Slot(str)
    def set_whisper_path(self, value):
        self._set_knowledge_config('whisper_path', value)

    @Slot(str)
    def set_ollama_url(self, value):
        self._set_knowledge_config('ollama_url', value)

    @Slot(str)
    def set_ollama_model(self, value):
        self._set_knowledge_config('ollama_model', value)

    def _set_knowledge_config(self, key, value):
        if 'knowledge_update' not in self.config:
            self.config['knowledge_update'] = {}
        self.config['knowledge_update'][key] = value
        self.save_config()
        self.configChanged.emit()

    @Slot(result=str)
    def get_model_provider(self):
        return self.config.get('model', {}).get('provider', 'ollama')

    @Slot(str)
    def set_model_provider(self, value):
        self._set_model_config('provider', value)

    @Slot(str, result=str)
    def get_ollama_base_url(self):
        return self.config.get('model', {}).get('ollama', {}).get('base_url', 'http://localhost:11434/api')

    @Slot(str)
    def set_ollama_base_url(self, value):
        self._set_provider_config('ollama', 'base_url', value)

    @Slot(str, result=str)
    def get_ollama_model_name(self):
        return self.config.get('model', {}).get('ollama', {}).get('model_name', 'qwen2:0.5b')

    @Slot(str)
    def set_ollama_model_name(self, value):
        self._set_provider_config('ollama', 'model_name', value)

    @Slot(str, result=str)
    def get_ollama_api_key(self):
        return self.config.get('model', {}).get('ollama', {}).get('api_key', '')

    @Slot(str)
    def set_ollama_api_key(self, value):
        self._set_provider_config('ollama', 'api_key', value)

    @Slot(str, result=str)
    def get_openai_base_url(self):
        return self.config.get('model', {}).get('openai', {}).get('base_url', 'https://api.openai.com/v1')

    @Slot(str)
    def set_openai_base_url(self, value):
        self._set_provider_config('openai', 'base_url', value)

    @Slot(str, result=str)
    def get_openai_model_name(self):
        return self.config.get('model', {}).get('openai', {}).get('model_name', 'gpt-3.5-turbo')

    @Slot(str)
    def set_openai_model_name(self, value):
        self._set_provider_config('openai', 'model_name', value)

    @Slot(str, result=str)
    def get_openai_api_key(self):
        return self.config.get('model', {}).get('openai', {}).get('api_key', '')

    @Slot(str)
    def set_openai_api_key(self, value):
        self._set_provider_config('openai', 'api_key', value)

    @Slot(str, result=str)
    def get_anthropic_base_url(self):
        return self.config.get('model', {}).get('anthropic', {}).get('base_url', 'https://api.anthropic.com/v1')

    @Slot(str)
    def set_anthropic_base_url(self, value):
        self._set_provider_config('anthropic', 'base_url', value)

    @Slot(str, result=str)
    def get_anthropic_model_name(self):
        return self.config.get('model', {}).get('anthropic', {}).get('model_name', 'claude-3-sonnet-20240229')

    @Slot(str)
    def set_anthropic_model_name(self, value):
        self._set_provider_config('anthropic', 'model_name', value)

    @Slot(str, result=str)
    def get_anthropic_api_key(self):
        return self.config.get('model', {}).get('anthropic', {}).get('api_key', '')

    @Slot(str)
    def set_anthropic_api_key(self, value):
        self._set_provider_config('anthropic', 'api_key', value)

    @Slot(str, result=str)
    def get_qwen_base_url(self):
        return self.config.get('model', {}).get('qwen', {}).get('base_url', 'https://dashscope.aliyuncs.com/api/v1')

    @Slot(str)
    def set_qwen_base_url(self, value):
        self._set_provider_config('qwen', 'base_url', value)

    @Slot(str, result=str)
    def get_qwen_model_name(self):
        return self.config.get('model', {}).get('qwen', {}).get('model_name', 'qwen2.5-7b-instruct')

    @Slot(str)
    def set_qwen_model_name(self, value):
        self._set_provider_config('qwen', 'model_name', value)

    @Slot(str, result=str)
    def get_qwen_api_key(self):
        return self.config.get('model', {}).get('qwen', {}).get('api_key', '')

    @Slot(str)
    def set_qwen_api_key(self, value):
        self._set_provider_config('qwen', 'api_key', value)

    @Slot(str, result=str)
    def get_deepseek_base_url(self):
        return self.config.get('model', {}).get('deepseek', {}).get('base_url', 'https://api.deepseek.com/v1')

    @Slot(str)
    def set_deepseek_base_url(self, value):
        self._set_provider_config('deepseek', 'base_url', value)

    @Slot(str, result=str)
    def get_deepseek_model_name(self):
        return self.config.get('model', {}).get('deepseek', {}).get('model_name', 'deepseek-chat')

    @Slot(str)
    def set_deepseek_model_name(self, value):
        self._set_provider_config('deepseek', 'model_name', value)

    @Slot(str, result=str)
    def get_deepseek_api_key(self):
        return self.config.get('model', {}).get('deepseek', {}).get('api_key', '')

    @Slot(str)
    def set_deepseek_api_key(self, value):
        self._set_provider_config('deepseek', 'api_key', value)

    def _set_model_config(self, key, value):
        if 'model' not in self.config:
            self.config['model'] = {}
        self.config['model'][key] = value
        self.save_config()
        self.configChanged.emit()

    def _set_provider_config(self, provider, key, value):
        if 'model' not in self.config:
            self.config['model'] = {}
        if provider not in self.config['model']:
            self.config['model'][provider] = {}
        self.config['model'][provider][key] = value
        self.save_config()
        self.configChanged.emit()

    @Slot(str, str, str, str)
    def save_custom_model(self, name, provider, url, api_key):
        if 'model' not in self.config:
            self.config['model'] = {}
        if 'custom_models' not in self.config['model']:
            self.config['model']['custom_models'] = {}
        if provider not in self.config['model']['custom_models']:
            self.config['model']['custom_models'][provider] = []
        
        model_config = {
            'name': name,
            'url': url,
            'api_key': api_key
        }
        
        self.config['model']['custom_models'][provider].append(model_config)
        self.save_config()
        self.configChanged.emit()
        print(f"Saved custom model: {name} for provider: {provider}")

    @Slot(str, result=list)
    def get_models_by_provider(self, provider):
        custom_models = self.config.get('model', {}).get('custom_models', {}).get(provider, [])
        return [model['name'] for model in custom_models]

    @Slot(str)
    def set_active_model(self, model_name):
        if 'model' not in self.config:
            self.config['model'] = {}
        self.config['model']['active_model'] = model_name
        self.save_config()
        self.configChanged.emit()
        print(f"Set active model: {model_name}")

    @Slot(result=str)
    def get_active_model(self):
        return self.config.get('model', {}).get('active_model', '')
