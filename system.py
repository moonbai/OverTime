# system.py
import sys
import traceback
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Frame, Button
from datetime import datetime
import webbrowser# 导入核心模块
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

        # 2. 业务模块 - 修正初始化
        self.modules['holiday'] = HolidayChecker(self.config_manager)
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

        #菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="设置", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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

            # 检查holiday状态
            holiday_status = "✅已集成" if self.modules['holiday'].calendar_available or self.modules['holiday'].holiday_config else "⚠️ 未配置"

            return get_html_template(leave_types, webhook_enabled, holiday_status)

        # 获取数据
        def get_data():
            records = self.data_manager.get_all_records()
            result = []
            for record in records[-10:]:
                if len(record) >= 8:
                    result.append({
                        '日期': record[0], '用户': record[1], '类型': record[2],
                        '加班时长': record[3], '请假类型': record[4], '请假时长': record[5],
                        '提交时间': record[6], '加班工资': record[7]
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

                # 计算加班工资
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
                        '加班类型': data['day_type'],
                        '加班时长': data.get('work_hours', '0'),
                        '请假类型': data.get('leave_type', '无'),
                        '请假时长': data.get('leave_hours', '无'),
                        '提交时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '加班工资': salary,
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

    def show_about(self):
        """显示关于信息 - 带GitHub链接"""
        def open_github():
            try:
                webbrowser.open("https://github.com/moonbai/OverTime")
            except:
                messagebox.showerror("错误", "无法打开浏览器")

        # 创建对话框
        about_window = Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("720x600")
        about_window.transient(self.root)
        about_window.grab_set()

        # 主框架
        main_frame = Frame(about_window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # 标题
        Label(main_frame, text="加班管理系统", font=("Arial", 18, "bold"), fg="#1976D2").pack(pady=5)
        Label(main_frame, text="v2.0", font=("Arial", 10), fg="#666666").pack()

        # 功能列表
        Label(main_frame, text="功能特性：", font=("Arial", 9, "bold"), anchor='w').pack(fill='x', pady=(15, 5))

        features = [
            "• 数据录入与管理",
            "• Web服务支持",
            "• Webhook推送",
            "• 智能节假日判断",
            "• 加班工资计算",
            "• API格式节假日数据"
        ]

        for feature in features:
            Label(main_frame, text=feature, font=("Arial", 9), anchor='w').pack(fill='x', padx=10)

        # GitHub链接区域
        github_frame = Frame(main_frame, bg="#F5F5F5", padx=10, pady=8)
        github_frame.pack(fill='x', pady=(15, 5))

        Label(github_frame, text="开源地址：", font=("Arial", 9, "bold"), bg="#F5F5F5").pack(anchor='w')

        # 可点击的链接按钮
        Button(github_frame, text="https://github.com/moonbai/OverTime",
               command=open_github,
               bg="#E3F2FD", fg="#1976D2", relief='flat', font=("Arial", 9, "underline"),
               cursor="hand2", padx=5).pack(anchor='w', pady=3)

        # 更新日志
        Label(main_frame, text="更新内容：", font=("Arial", 9, "bold"), anchor='w').pack(fill='x', pady=(10, 5))

        updates = [
            "• 支持API格式节假日数据",
            "• 按detailsType精确分类",
            "• 普通节假日统计为休息日",
            "• 三倍工资节假日单独识别"
        ]

        for update in updates:
            Label(main_frame, text=update, font=("Arial", 8), anchor='w').pack(fill='x', padx=10)

        # 底部
        Label(main_frame, text="\n© 加班管理系统", font=("Arial", 8), fg="#666666").pack(pady=10)

        # 按钮
        Button(main_frame, text="关闭", command=about_window.destroy,
               bg="#757575", fg="white", width=10).pack(pady=5)

        # 居中窗口
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f"{width}x{height}+{x}+{y}")

    def on_closing(self):
        """程序关闭时的清理"""
        try:
            if self.modules['web_service'].is_running():
                if messagebox.askyesno("确认", "Web服务正在运行，确定要退出吗？"):
                    self.stop_web_service()
                    self.root.destroy()
            else:
                self.root.destroy()
        except:
            self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("加班管理系统")
        root.geometry("800x650")
        root.minsize(750, 600)

        system = OvertimeSystem(root)
        root.mainloop()
    except Exception as e:
        print("\n============================================================")
        print("启动失败！")
        print("============================================================")
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
