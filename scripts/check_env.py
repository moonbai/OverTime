#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检测工具
功能：检查系统环境、依赖、数据文件等
"""

import sys
import os
import platform

def check_python():
    """检查Python版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 6:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
    return False, f"Python {version.major}.{version.minor} 不支持（需要3.6+）"

def check_dependency(package_name, import_name=None):
    """检查依赖包"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True, "已安装"
    except ImportError:
        return False, "未安装"

def check_data_files():
    """检查数据文件"""
    data_dir = "data"
    csv_file = os.path.join(data_dir, "overtime_records.csv")

    if not os.path.exists(data_dir):
        return False, "data目录不存在"
    if not os.path.exists(csv_file):
        return False, "CSV文件不存在"

    file_size = os.path.getsize(csv_file)
    return True, f"正常 ({file_size/1024:.1f} KB)"

def check_config():
    """检查配置文件"""
    if os.path.exists("config.json"):
        return True, "存在"
    return False, "不存在"

def main():
    print("="*60)
    print("加班管理系统 - 环境检测工具")
    print("="*60)

    # 系统信息
    print(f"\n系统环境：")
    print(f"  操作系统: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version.split()[0]}")

    # Python版本检查
    py_ok, py_msg = check_python()
    print(f"\nPython版本: {py_msg}")
    if not py_ok:
        print("❌ 请升级Python到3.6+")
        return

    # 依赖检查
    print(f"\n依赖检查：")
    deps = [
        ("tkcalendar", "tkcalendar", "必需"),
        ("workalendar", "workalendar", "推荐"),
        ("openpyxl", "openpyxl", "可选")
    ]

    all_installed = True
    for pkg, import_name, level in deps:
        installed, msg = check_dependency(pkg, import_name)
        status = "✅" if installed else "❌"
        print(f"  {pkg:15} {msg:10} {level:6} {status}")
        if not installed and level == "必需":
            all_installed = False

    # 文件检查
    print(f"\n文件检查：")
    config_ok, config_msg = check_config()
    data_ok, data_msg = check_data_files()

    print(f"  配置文件: {'✅' if config_ok else '❌'} {config_msg}")
    print(f"  数据文件: {'✅' if data_ok else '❌'} {data_msg}")

    # 总结
    print("\n" + "="*60)
    if all_installed and config_ok and data_ok:
        print("✅ 环境检查通过，可以正常运行！")
    else:
        print("❌ 环境存在问题：")
        if not all_installed:
            print("  - 缺少必需依赖，请运行: python scripts/install_deps.py")
        if not config_ok:
            print("  - 缺少配置文件，首次运行会自动生成")
        if not data_ok:
            print("  - 缺少数据目录，首次运行会自动生成")
    print("="*60)

if __name__ == "__main__":
    main()
