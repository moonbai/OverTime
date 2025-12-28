#!/usr/bin/env python3
# install.py - 跨平台依赖安装脚本

import sys
import subprocess
import platform

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def check_python():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 错误：需要 Python 3.7+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}环境正常")
    return True

def install_package(package, description):
    """安装单个包"""
    print(f"\n📦 安装 {description}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package,
             "--trusted-host", "pypi.org",
             "--trusted-host", "files.pythonhosted.org"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"✅ {description} 安装成功")
            return True
        else:
            print(f"⚠️  {description} 安装失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} 安装出错: {e}")
        return False

def main():
    print_header("加班管理系统 - 依赖安装脚本")

    # 1. 检查Python
    if not check_python():
        input("\n按回车键退出...")
        sys.exit(1)

    print("\n[1/3] 必需依赖")
    print("✅ 纯Python标准库实现，无需额外安装")

    print("\n[2/3] 可选依赖")
    print("以下依赖提供增强功能，但非必需：")
    print("  1. workalendar - 增强的节假日判断（支持中国节假日）")
    print("  2. openpyxl - Excel导出功能")
    print("  3. 全部安装")
    print("  4. 跳过（使用内置功能）")

    choice = input("\n请选择 (1/2/3/4): ").strip()

    packages = {
        '1': [('workalendar', 'workalendar'), ('workalendar', '节假日判断增强')],
        '2': [('openpyxl', 'openpyxl'), ('openpyxl', 'Excel导出功能')],
        '3': [
            ('workalendar', 'workalendar'), ('workalendar', '节假日判断增强'),
            ('openpyxl', 'openpyxl'), ('openpyxl', 'Excel导出功能')
        ],
        '4': []
    }

    if choice in packages:
        to_install = packages[choice]
        if not to_install:
            print("\n⚠️  跳过可选依赖安装")
            print("    - 节假日判断将使用内置数据（2024/2026年）")
            print("    - 无法导出Excel文件")
        else:
            success_count = 0
            for package, desc in to_install:
                if install_package(package, desc):
                    success_count += 1
                    print(f"\n✅ 安装完成！成功 {success_count}/{len(to_install)}")
    else:
        print("\n❌ 无效选择，跳过安装")

    print_header("安装完成")
    print("\n运行程序: python main.py")
    print("\n功能说明：")
    print("✅ 基础功能（无需任何依赖）")
    print("    - 加班记录管理")
    print("    - 请假管理")
    print("    - 数据导入/导出")
    print("    - Web服务填报")
    print("    - Webhook同步")
    print("\n  ⚠️ 可选功能（需要安装依赖）")
    print("    - 增强节假日判断（workalendar）")
    print("    - Excel导出（openpyxl）")

    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
