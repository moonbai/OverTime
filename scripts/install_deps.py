#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本
功能：一键安装所有可选依赖
"""

import subprocess
import sys
import os

def install_package(package_name, description):
    """安装单个包"""
    print(f"\n📦正在安装 {package_name} - {description}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ {package_name} 安装成功")
            return True
        else:
            print(f"❌ {package_name} 安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装异常: {e}")
        return False

def check_installed(package_name):
    """检查包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("="*60)
    print("加班管理系统 - 依赖安装工具")
    print("="*60)

    packages = [
        ("tkcalendar", "日历选择器（必需）"),
        ("workalendar", "节假日判断（推荐）"),
        ("openpyxl", "Excel导出（可选）")
    ]

    print("\n当前环境检测：")
    for pkg, desc in packages:
        status = "✅ 已安装" if check_installed(pkg.replace("-", "_")) else "❌ 未安装"
        print(f"  {pkg:15} - {status}")

    print("\n请选择操作：")
    print("1. 安装所有依赖")
    print("2. 仅安装必需依赖 (tkcalendar)")
    print("3. 退出")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    if choice == "1":
        for pkg, desc in packages:
            if not check_installed(pkg.replace("-", "_")):
                install_package(pkg, desc)
    elif choice == "2":
        if not check_installed("tkcalendar"):
            install_package("tkcalendar", "日历选择器")
 else:
            print("✅ tkcalendar 已安装")
    elif choice == "3":
        print("👋 退出安装程序")
        return

    print("\n" + "="*60)
    print("✅ 安装完成！")
    print("="*60)

if __name__ == "__main__":
    main()
