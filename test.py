# test.py
import sys
import os
import json

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

from core.config import ConfigManager
from modules.holiday import HolidayChecker

print("="*80)
print("🔧 详细调试测试")
print("="*80)

# 1.检查配置文件
config_file = os.path.join("modules", "holiday.json")
print(f"\n1.检查文件: {config_file}")
if os.path.exists(config_file):
    print("   ✓ 文件存在")
    with open(config_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    print(f"   原始数据类型: {type(raw_data)}")
    print(f"   原始数据键: {list(raw_data.keys()) if isinstance(raw_data, dict) else '是列表'}")

    # 检查是否是API格式
    if isinstance(raw_data, dict) and "data" in raw_data:
        print("   ✓ 检测到API格式，data字段存在")
        data = raw_data["data"]
        print(f"   data字段类型: {type(data)}")
        if isinstance(data, list) and len(data) > 0:
            print(f"   data[0]键: {list(data[0].keys())}")
            if "days" in data[0]:
                print(f"   ✓ days字段存在，包含 {len(data[0]['days'])} 天数据")
                # 打印前两个日期
                for i, day in enumerate(data[0]['days'][:2]):
                    print(f"     {i+1}. {day['date']}: type={day['type']}, detailsType={day['detailsType']}, typeDes={day['typeDes']}")
else:
    print("   ✗ 文件不存在")
    sys.exit(1)

# 2. 创建配置和检查器
print("\n2. 创建检查器")
config = ConfigManager()
config.set('use_builtin_holiday', True)
config.save_config()
print(f"   use_builtin_holiday: {config.get('use_builtin_holiday')}")

checker = HolidayChecker(config)

# 3. 检查加载的数据
print("\n3. 检查加载的数据")
print(f"   holiday_data类型: {type(checker.holiday_data)}")
print(f"   holiday_data键: {list(checker.holiday_data.keys()) if checker.holiday_data else '空'}")

if checker.holiday_data:
    for year, months in checker.holiday_data.items():
        print(f"   年份 {year}: {len(months)} 个月")
        for month_day, config in list(months.items())[:2]:
            print(f"     {month_day}: type={config['type']}, detailsType={config['detailsType']}")

# 4. 测试单个日期
print("\n4. 测试日期 2026-01-01")
info = checker.get_holiday_info("2026-01-01")
print(f"   Info: {info}")

day_type, reason = checker.get_day_type("2026-01-01")
print(f"   Result: {day_type}, {reason}")

# 5. 验证结果
print("\n5. 验证结果")
if info['type'] == 2 and info['detailsType'] == 3:
    print("   ✅ 正确：type=2, detailsType=3")
    if day_type == "节假日" and "三倍" in reason:
        print("   ✅ 正确：返回节假日(三倍)")
    else:
        print(f"   ❌ 错误：应返回节假日(三倍)，实际返回 {day_type}, {reason}")
else:
    print(f"   ❌ 错误：应为 type=2, detailsType=3，实际为 type={info['type']}, detailsType={info['detailsType']}")
    print("可能原因：")
    print("   - JSON数据格式不正确")
    print("   - 日期格式不匹配")
    print("   - 配置未生效")

print("\n" + "="*80)
