#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据备份脚本
功能：手动备份数据文件
"""

import os
import shutil
import datetime
import sys

def backup_data():
    """执行备份"""
    data_dir = "data"
    backup_dir = os.path.join(data_dir, "backup")
    csv_file = os.path.join(data_dir, "overtime_records.csv")

    # 检查源文件
    if not os.path.exists(csv_file):
        print(f"❌ 未找到数据文件: {csv_file}")
        return False

    # 创建备份目录
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✓ 创建备份目录: {backup_dir}")

    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"overtime_records_{timestamp}.csv")

    # 执行备份
    try:
        shutil.copy2(csv_file, backup_file)
        file_size = os.path.getsize(backup_file)
        print(f"✅ 备份成功: {backup_file}")
        print(f"   文件大小: {file_size/1024:.2f} KB")
        return True
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False

def list_backups():
    """列出所有备份"""
    backup_dir = os.path.join("data", "backup")
    if not os.path.exists(backup_dir):
        print("暂无备份文件")
        return

    backups = []
    for f in os.listdir(backup_dir):
        if f.startswith("overtime_records_") and f.endswith(".csv"):
            fpath = os.path.join(backup_dir, f)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
            size = os.path.getsize(fpath)
            backups.append((f, mtime, size))

    if not backups:
        print("暂无备份文件")
        return

    print("\n现有备份：")
    for name, mtime, size in backups:
        print(f"  {name} | {mtime.strftime('%Y-%m-%d %H:%M')} | {size/1024:.1f} KB")

def restore_backup(backup_name):
    """恢复备份"""
    backup_dir = os.path.join("data", "backup")
    backup_file = os.path.join(backup_dir, backup_name)
    csv_file = os.path.join("data", "overtime_records.csv")

    if not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_name}")
        return False

    try:
        # 先备份当前数据
        if os.path.exists(csv_file):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = os.path.join(backup_dir, f"overtime_records_current_{timestamp}.csv")
            shutil.copy2(csv_file, current_backup)
            print(f"✓已备份当前数据: {current_backup}")

        # 恢复        shutil.copy2(backup_file, csv_file)
        print(f"✅ 恢复成功: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def main():
    print("="*60)
    print("加班管理系统 - 数据备份工具")
    print("="*60)

    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "list":
            list_backups()
        elif action == "backup":
            backup_data()
        elif action == "restore" and len(sys.argv) > 2:
            restore_backup(sys.argv[2])
        else:
            print("用法:")
            print("  python scripts/backup_data.py backup - 创建备份")
            print("  python scripts/backup_data.py list     - 列出备份")
            print("  python scripts/backup_data.py restore <文件名> - 恢复备份")
    else:
        print("\n选项：")
        print("1. 创建备份")
        print("2. 列出备份")
        print("3. 恢复备份")
        print("4. 退出")

        choice = input("\n请输入选项 (1/2/3/4): ").strip()

        if choice == "1":
            backup_data()
        elif choice == "2":
            list_backups()
        elif choice == "3":
            list_backups()
            name = input("\n请输入要恢复的备份文件名: ").strip()
            if name:
                restore_backup(name)
        else:
            print("👋 退出")

    print("="*60)

if __name__ == "__main__":
    main()
