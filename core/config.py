# core/config.py
import json
import os
from typing import Dict, Any

class ConfigManager:
    """统一配置管理器"""

    DEFAULT_CONFIG = {
        'last_user': '',
        'default_hours': '8',
        'page_size': 10,
        'web_port': 8080,
        'leave_types': ['事假', '病假', '年假', '婚假', '产假'],
        'deduct_rest_day_hours': True,
        'overtime_pay': {
            'enabled': False,
            'hourly_wage': 50.0,  # 新增：小时工资
            'weekday_rate': 1.5,
            'weekend_rate': 2.0,
            'holiday_rate': 3.0,
            'deduct_types': ['事假']  # 新增：扣除工时的请假类型
        },
        'webhook': {
            'enabled': False,
            'url': '',
            'headers': '{}',
            'timeout': 10,
            'retry': 3,
            'sync_mode': 'sync'
        },
        'modules': {
            'overtime': True,
            'salary': True,
            'leave': True,
            'webhook': True,
            'web_service': True,
            'holiday': True
        }
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置，缺失的使用默认值"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                merged = self.DEFAULT_CONFIG.copy()
                self._deep_merge(merged, user_config)
                print(f"✓ 配置加载成功")
                return merged
            except Exception as e:
                print(f"⚠ 配置加载失败，使用默认配置: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            print("ℹ 未找到配置文件，使用默认配置")
            return self.DEFAULT_CONFIG.copy()

    def _deep_merge(self, default, user):
        """深度合并配置字典"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._deep_merge(default[key], value)
            else:
                default[key] = value

    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✓ 配置已保存")
            return True
        except Exception as e:
            print(f"✗ 保存配置失败: {e}")
            return False

    def get(self, key: str, default=None):
        """获取配置项，支持点号路径"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value):
        """设置配置项，支持点号路径"""
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()

    def is_module_enabled(self, module_name: str) -> bool:
        """检查模块是否启用"""
        return self.get(f'modules.{module_name}', True)
