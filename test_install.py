# test_install.py
try:
    import workalendar
    print("✅ workalendar 已安装")
except ImportError:
    print("⚠️  workalendar 未安装，使用内置数据")

try:
    import openpyxl
    print("✅ openpyxl 已安装")
except ImportError:
    print("⚠️  openpyxl 未安装，无法导出Excel")

print("\n基础功能测试...")
from core.config import ConfigManager
from core.data_manager import DataManager
print("✅ 基础模块加载成功")
