# system.py
import sys
import traceback
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# 导入核心模块
from core.config import ConfigManager
from core.data_manager import DataManager

# 导入业务模块
from modules.holiday import HolidayChecker
from modules.overtime import OvertimeModule
from modules.salary import SalaryModule
from modules.leave import LeaveModule
from modules.webhook import WebhookModule
from modules.web_service.server import WebServiceModule
from modules.web_service.templates import get_html_template

# 导入UI模块
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog

class OvertimeSystem:
    """系统集成器 - 负责模块连接和生命周期管理"""

    def __init__(self, root):
        self.root = root
        self.modules = {}
        self.init_system()

    def init_system(self):
        """初始化系统和所有模块"""
        print("="*60)
        print("加班管理系统")
        print("="*60)

        # 1. 核心组件
        self.config_manager = ConfigManager()
        self.data_manager = DataManager()

        # 创建数据文件
        try:
            self.data_manager.create_file_if_not_exists()
        except Exception as e:
            messagebox.showerror("错误", str(e))
            sys.exit(1)

        # 2. 业务模块
        self.modules['holiday'] = HolidayChecker(use_workalendar=True)
        self.modules['overtime'] = OvertimeModule(
            self.data_manager,
            self.modules['holiday'],
            self.config_manager
        )
        self.modules['salary'] = SalaryModule(self.config_manager)
        self.modules['leave'] = LeaveModule(self.config_manager)
        self.modules['webhook'] = WebhookModule(self.config_manager)
        self.modules['web_service'] = WebServiceModule(self.config_manager)

        # 3. 设置Web服务回调
        self.setup_web_callbacks()

        # 4. 创建UI
        self.main_window = MainWindow(
            self.root,
            self.config_manager,
            self.data_manager,
            self.modules,
            self.open_settings,
            self.start_web_service,
            self.stop_web_service
        )

        print("="*60)
        print("✓ 系统初始化完成")
        print("="*60)

    def setup_web_callbacks(self):
        """设置Web服务回调"""
        web_service = self.modules['web_service']

        # 获取HTML页面
        def get_html():
            leave_types = self.config_manager.get('leave_types', ['事假', '病假', '年假', '婚假', '产假'])
            webhook_enabled = self.config_manager.get('webhook.enabled', False)
            holiday_info = "✅ 已集成" if self.modules['holiday'] else "⚠️ 未配置"

            return get_html_template(leave_types, webhook_enabled, holiday_info)

        # 获取数据
        def get_data():
            records = self.data_manager.get_all_records()
            result = []
            for record in records[-10:]:
                if len(record) >= 8:
                    result.append({
                        '日期': record[0], '用户': record[1], '类型': record[2],
                        '工作时长': record[3], '请假类型': record[4], '请假时长': record[5],
                        '提交时间': record[6], '工资': record[7]
                    })
            return result

        # 检查日期
        def check_date(date):
            return self.modules['holiday'].get_day_type(date)

        # 提交记录
        def submit_record(data):
            try:
                # 处理请假
                if data.get('is_leave'):
                    leave_result = self.modules['leave'].process_leave(data)
                    data.update(leave_result)
                else:
                    data['leave_type'] = '无'
                    data['leave_hours'] = '无'

                # 计算工资
                salary = "0"
                if data.get('is_leave'):
                    if self.config_manager.get('deduct_rest_day_hours', True):
                        salary = self.modules['salary'].calculate(data['date'], data.get('leave_hours', '0'), data['day_type'])
                else:
                    salary = self.modules['salary'].calculate(data['date'], data.get('work_hours', '0'), data['day_type'])

                data['salary'] = salary
                data['calculate_salary'] = True

                # 提交记录
                success, message, record = self.modules['overtime'].submit_overtime(data)

                # Webhook同步（网页提交也会触发）
                if success and self.config_manager.get('webhook.enabled', False):
                    webhook_data = {
                        '类型': '网页填报',
                        '日期': data['date'],
                        '用户': data['user'],
                        '工作类型': data['day_type'],
                        '工作时长': data.get('work_hours', '0'),
                        '请假类型': data.get('leave_type', '无'),
                        '请假时长': data.get('leave_hours', '无'),
                        '提交时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '工资': salary,
                        '提交方式': data.get('submit_method', '网页填报')
                    }
                    self.modules['webhook'].send(webhook_data)

                return success, message, record

            except Exception as e:
                return False, str(e), None

        web_service.register_callback('get_html', get_html)
        web_service.register_callback('get_data', get_data)
        web_service.register_callback('check_date', check_date)
        web_service.register_callback('submit_record', submit_record)

    def open_settings(self):
        """打开设置对话框"""
        def on_save():
            self.config_manager.load_config()
            self.main_window.on_config_changed()

        SettingsDialog(self.root, self.config_manager, on_save)

    def start_web_service(self):
        """启动Web服务"""
        success, message = self.modules['web_service'].start()
        if success:
            self.main_window.update_web_status(message, True)
        else:
            messagebox.showerror("启动失败", message)

    def stop_web_service(self):
        """停止Web服务"""
        success, message = self.modules['web_service'].stop()
        if success:
            self.main_window.update_web_status("服务已停止", False)
        else:
            messagebox.showerror("停止失败", message)
