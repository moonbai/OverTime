#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本 - 增强版
功能：一键安装所有可选依赖
支持：多平台Webhook依赖
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
        ("requests", "HTTP请求库（必需，支持Webhook）"),
        ("workalendar", "节假日判断（推荐）"),
        ("openpyxl", "Excel导出（可选）")
    ]

    print("\n当前环境检测：")
    for pkg, desc in packages:
        status = "✅ 已安装" if check_installed(pkg.replace("-", "_")) else "❌ 未安装"
        print(f"  {pkg:15} - {status} - {desc}")

    print("\n请选择操作：")
    print("1. 安装所有依赖（推荐）")
    print("2. 仅安装必需依赖 (tkcalendar + requests)")
    print("3. 自定义安装")
    print("4. 退出")

    choice = input("\n请输入选项 (1/2/3/4): ").strip()

    if choice == "1":
        for pkg, desc in packages:
            if not check_installed(pkg.replace("-", "_")):
                install_package(pkg, desc)
            else:
                print(f"✅ {pkg} 已安装，跳过")

    elif choice == "2":
        for pkg, desc in packages[:2]:  # 前两个是必需的
            if not check_installed(pkg.replace("-", "_")):
                install_package(pkg, desc)
            else:
                print(f"✅ {pkg} 已安装，跳过")

    elif choice == "3":
        print("\n可选包：")
        for i, (pkg, desc) in enumerate(packages[2:], 1):
            print(f"  {i}. {pkg} - {desc}")

        selections = input("\n请输入要安装的编号（多个用逗号分隔，如 1,2）: ").strip()
        if selections:
            try:
                indices = [int(x.strip()) - 1 for x in selections.split(",")]
                for idx in indices:
                    if 0 <= idx < len(packages):
                        pkg, desc = packages[idx]
                        if not check_installed(pkg.replace("-", "_")):
                            install_package(pkg, desc)
                        else:
                            print(f"✅ {pkg} 已安装，跳过")
            except:
                print("❌ 无效的输入")

    elif choice == "4":
        print("👋 退出安装程序")
        return

    else:
        print("❌ 无效选项")
        return

    print("\n" + "="*60)
    print("✅ 安装完成！")
    print("\n重要说明：")
    print("  - tkcalendar: 必需，提供日历选择器")
    print("  - requests: 必需，支持Web服务和Webhook")
    print("  - workalendar:推荐，增强节假日判断")
    print("  - openpyxl: 可选，支持Excel导出")
    print("="*60)

if __name__ == "__main__":
    main()
