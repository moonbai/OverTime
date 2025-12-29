# ui/settings_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import json

class SettingsDialog:
    """系统设置对话框"""

    def __init__(self, parent, config_manager, on_save_callback=None):
        self.parent = parent
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("系统设置")
        self.dialog.geometry("650x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.center_window()
        self.create_widgets()
        self.load_config()

    def center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 基础设置
        self.basic_frame = ttk.Frame(notebook)
        notebook.add(self.basic_frame, text="基础设置")
        self.create_basic_settings()

        # 请假配置
        self.leave_frame = ttk.Frame(notebook)
        notebook.add(self.leave_frame, text="请假配置")
        self.create_leave_settings()

        # 加班工资
        self.salary_frame = ttk.Frame(notebook)
        notebook.add(self.salary_frame, text="加班工资")
        self.create_salary_settings()

        # 节假日数据源
        self.holiday_frame = ttk.Frame(notebook)
        notebook.add(self.holiday_frame, text="节假日数据")
        self.create_holiday_settings()

        # Web服务/Webhook
        self.web_frame = ttk.Frame(notebook)
        notebook.add(self.web_frame, text="Web服务/Webhook")
        self.create_web_settings()

        # 按钮
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(button_frame, text="保存并关闭", command=self.save_and_close,
                 bg="#4CAF50", fg="white", width=15).pack(side='left', padx=5)

        tk.Button(button_frame, text="重置为默认", command=self.reset_to_default,
                 bg="#FF9800", fg="white", width=15).pack(side='left', padx=5)

        tk.Button(button_frame, text="取消", command=self.dialog.destroy,
                 bg="#E0E0E0", width=15).pack(side='right', padx=5)

    def create_basic_settings(self):
        frame = self.basic_frame

        tk.Label(frame, text="默认用户:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.basic_user = tk.Entry(frame, width=25)
        self.basic_user.grid(row=0, column=1, sticky='ew', padx=10, pady=5)

        tk.Label(frame, text="默认加班时长:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.basic_hours = tk.Entry(frame, width=25)
        self.basic_hours.grid(row=1, column=1, sticky='ew', padx=10, pady=5)

        tk.Label(frame, text="每页显示记录数:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.basic_page_size = tk.Spinbox(frame, from_=5, to=50, width=25)
        self.basic_page_size.grid(row=2, column=1, sticky='ew', padx=10, pady=5)

        # 安装依赖按钮
        install_frame = tk.Frame(frame)
        install_frame.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=10)

        tk.Label(install_frame, text="扩展功能:", font=("Arial", 9, "bold")).pack(side='left', padx=(0, 10))
        tk.Button(install_frame, text="安装 chinesecalendar", command=self.install_chinesecalendar,
                 bg="#FF9800", fg="white", width=20).pack(side='left', padx=5)
        tk.Button(install_frame, text="安装 openpyxl", command=self.install_openpyxl,
                 bg="#FF9800", fg="white", width=15).pack(side='left', padx=5)

        tk.Label(frame, text="说明：chinesecalendar增强节假日判断，openpyxl支持Excel导出",
                font=("Arial", 8), fg="#666666").grid(row=4, column=0, columnspan=2, sticky='w', padx=10, pady=5)

    def create_leave_settings(self):
        frame = self.leave_frame

        # 请假类型
        tk.Label(frame, text="请假类型配置:", font=("Arial", 9, "bold")).pack(anchor='w', padx=10, pady=5)
        self.leave_types_text = scrolledtext.ScrolledText(frame, width=50, height=6, font=("Arial", 9))
        self.leave_types_text.pack(fill='x', padx=10, pady=5)

        # 扣除规则
        tk.Label(frame, text="工时扣除规则:", font=("Arial", 9, "bold")).pack(anchor='w', padx=10, pady=(10, 5))

        deduct_frame = tk.Frame(frame)
        deduct_frame.pack(fill='x', padx=10, pady=5)

        self.deduct_vars = {}
        leave_types = self.config_manager.get('leave_types', ['事假', '病假', '年假', '婚假', '产假'])

        for leave_type in leave_types:
            var = tk.BooleanVar()
            self.deduct_vars[leave_type] = var
            cb = tk.Checkbutton(deduct_frame, text=leave_type, variable=var)
            cb.pack(side='left', padx=5, pady=2)

        tk.Label(frame, text="提示：勾选的请假类型将扣除休息日工时",
                font=("Arial", 8), fg="#666666").pack(anchor='w', padx=10, pady=5)

        tk.Button(frame, text="加载当前配置", command=self.load_current_leave_types,
                 bg="#2196F3", fg="white", width=15).pack(pady=5)

    def create_salary_settings(self):
        frame = self.salary_frame

        #基础配置
        base_frame = tk.Frame(frame)
        base_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(base_frame, text="加班工资计算:", font=("Arial", 9, "bold")).pack(side='left', padx=(0, 10))
        self.salary_enabled = tk.BooleanVar()
        tk.Checkbutton(base_frame, text="启用", variable=self.salary_enabled,
                      command=self.toggle_salary_inputs).pack(side='left')

        # 小时加班工资
        wage_frame = tk.Frame(frame)
        wage_frame.pack(fill='x', padx=10, pady=10)
        tk.Label(wage_frame, text="小时加班工资:", font=("Arial", 9, "bold")).pack(side='left', padx=(0, 10))
        self.hourly_wage = tk.Entry(wage_frame, width=10)
        self.hourly_wage.pack(side='left')
        tk.Label(wage_frame, text="元/小时", font=("Arial", 9)).pack(side='left', padx=5)

        # 费率配置
        rate_frame = tk.LabelFrame(frame, text="倍率配置", font=("Arial", 9, "bold"))
        rate_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(rate_frame, text="工作日:", font=("Arial", 9)).pack(side='left', padx=5)
        self.salary_weekday = tk.Entry(rate_frame, width=8)
        self.salary_weekday.pack(side='left', padx=5)

        tk.Label(rate_frame, text="休息日:", font=("Arial", 9)).pack(side='left', padx=5)
        self.salary_weekend = tk.Entry(rate_frame, width=8)
        self.salary_weekend.pack(side='left', padx=5)

        tk.Label(rate_frame, text="节假日:", font=("Arial", 9)).pack(side='left', padx=5)
        self.salary_holiday = tk.Entry(rate_frame, width=8)
        self.salary_holiday.pack(side='left', padx=5)

        tk.Label(frame, text="计算公式：加班工资 = 小时加班工资 × 时长 × 倍率",
                font=("Arial", 8), fg="#666666").pack(anchor='w', padx=10, pady=10)

        tk.Label(frame, text="示例：小时加班工资50元，工作日加班8小时 = 50×8×1.0 = 400元",
                font=("Arial", 8), fg="#666666").pack(anchor='w', padx=10, pady=0)

    def create_holiday_settings(self):
        """节假日数据源设置"""
        frame = self.holiday_frame

        # 数据源选择
        tk.Label(frame, text="数据源:", font=("Arial", 9, "bold")).pack(anchor='w', padx=10, pady=5)

        self.holiday_source = tk.StringVar()
        source_frame = tk.Frame(frame)
        source_frame.pack(fill='x', padx=10, pady=5)

        tk.Radiobutton(source_frame, text="内置数据 (modules/holiday.json)",
                      variable=self.holiday_source, value="builtin").pack(side='left', padx=5)

        tk.Radiobutton(source_frame, text="chinese_calendar",
                      variable=self.holiday_source, value="chinese").pack(side='left', padx=5)

        # 操作按钮
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(btn_frame, text="获取第三方JSON", command=self.get_official_json,
                 bg="#9C27B0", fg="white", width=20).pack(side='left', padx=5)

        tk.Button(btn_frame, text="安装 chinese_calendar", command=self.install_chinesecalendar,
                 bg="#FF9800", fg="white", width=20).pack(side='left', padx=5)

        # 状态显示
        self.holiday_status = tk.Label(frame, text="", font=("Arial", 8), fg="#666666")
        self.holiday_status.pack(anchor='w', padx=10, pady=5)

        # 说明
        tk.Label(frame, text="说明：\n• 内置数据: 从第三方API获取年度Json信息并保存到 modules/holiday.json文件内\n• chinese_calendar: 安装依赖库自动判断\n\n推荐采用第三方数据源判定更准确，目前依赖库因部分数据确实无法准确区分三倍工资法定节假日及普通节假日",
                font=("Arial", 8), fg="#666666").pack(anchor='w', padx=10, pady=5)

    def create_web_settings(self):
        frame = self.web_frame

        # Web服务配置
        tk.Label(frame, text="Web服务端口:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.web_port = tk.Entry(frame, width=25)
        self.web_port.grid(row=0, column=1, sticky='ew', padx=10, pady=5)

        # Webhook平台选择
        tk.Label(frame, text="Webhook平台:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky='w', padx=10, pady=5)

        # 获取平台列表
        from modules.webhook import WebhookModule
        wb = WebhookModule(self.config_manager)
        platforms = wb.get_supported_platforms()
        platform_names = [f"{name} - {desc}" for _, name, desc in platforms]

        self.webhook_platform = ttk.Combobox(frame, values=platform_names,
                                            width=28, state="readonly")
        self.webhook_platform.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        self.webhook_platform.bind("<<ComboboxSelected>>", self.on_platform_change)

        # Webhook URL
        tk.Label(frame, text="Webhook URL:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.webhook_url = tk.Entry(frame, width=40)
        self.webhook_url.grid(row=2, column=1, sticky='ew', padx=10, pady=5)

        # URL提示
        self.url_hint_label = tk.Label(frame, text="", font=("Arial", 8), fg="#666666")
        self.url_hint_label.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=2)

        # 格式说明
        self.format_info = tk.Label(frame, text="", font=("Arial", 8, "italic"), fg="#1976D2")
        self.format_info.grid(row=4, column=0, columnspan=2, sticky='w', padx=10, pady=2)

        # 启用开关
        tk.Label(frame, text="Webhook状态:", font=("Arial", 9, "bold")).grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.webhook_enabled = tk.BooleanVar()
        tk.Checkbutton(frame, text="启用Webhook同步", variable=self.webhook_enabled).grid(row=5, column=1, sticky='w', padx=10, pady=5)

        # 高级设置
        advanced_frame = tk.LabelFrame(frame, text="高级设置", font=("Arial", 9, "bold"))
        advanced_frame.grid(row=6, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        tk.Label(advanced_frame, text="超时(秒):").pack(side='left', padx=5)
        self.webhook_timeout = tk.Entry(advanced_frame, width=8)
        self.webhook_timeout.pack(side='left', padx=5)

        tk.Label(advanced_frame, text="重试次数:").pack(side='left', padx=5)
        self.webhook_retry = tk.Entry(advanced_frame, width=8)
        self.webhook_retry.pack(side='left', padx=5)

        tk.Label(advanced_frame, text="同步模式:").pack(side='left', padx=5)
        self.webhook_mode = ttk.Combobox(advanced_frame, values=["sync", "async"], width=8, state="readonly")
        self.webhook_mode.pack(side='left', padx=5)

        # 测试按钮
        tk.Button(frame, text="测试Webhook连接", command=self.test_webhook,
                 bg="#FF9800", fg="white", width=20).grid(row=7, column=0, columnspan=2, pady=10)

        # 平台对比说明
        compare_frame = tk.LabelFrame(frame, text="平台对比", font=("Arial", 9, "bold"))
        compare_frame.grid(row=8, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

        compare_text = """飞书/钉钉/企业微信:适合国内企业，功能丰富
Slack: 适合国际团队，集成众多应用
自定义: 适合有特殊需求或自建服务"""

        tk.Label(compare_frame, text=compare_text, font=("Arial", 8), justify='left').pack(anchor='w', padx=5, pady=5)

    def on_platform_change(self, event):
        """平台选择变化时更新说明"""
        platform_text = self.webhook_platform.get()
        platform_map = {
            '飞书 (Feishu)': 'feishu',
            '钉钉 (DingTalk)': 'dingtalk',
            '企业微信 (WeChat Work)': 'wechat',
            'Lark (飞书国际版)': 'lark',
            'Slack': 'slack',
            '自定义 (Custom)': 'custom'
        }

        platform_key = platform_map.get(platform_text.split(' - ')[0] if ' - ' in platform_text else platform_text,
                                        'feishu')

        try:
            from modules.webhook import WebhookModule
            wb = WebhookModule(self.config_manager)

            hint = wb.get_url_hint(platform_key)
            self.url_hint_label.config(text=f"URL格式: {hint}")

            format_info = wb.get_format_info(platform_key)
            self.format_info.config(text=f"数据格式: {format_info}")
        except Exception as e:
            print(f"⚠️ 更新平台说明失败: {e}")

    def load_config(self):
        # 基础设置
        self.basic_user.insert(0, self.config_manager.get('last_user', ''))
        self.basic_hours.insert(0, self.config_manager.get('default_hours', '8'))
        self.basic_page_size.delete(0, tk.END)
        self.basic_page_size.insert(0, str(self.config_manager.get('page_size', 10)))

        # 请假类型
        leave_types = self.config_manager.get('leave_types', ['事假', '病假', '年假', '婚假', '产假'])
        self.leave_types_text.insert('1.0', '\n'.join(leave_types))

        # 扣除规则
        deduct_types = self.config_manager.get('overtime_pay.deduct_types', ['事假'])
        for leave_type in leave_types:
            if leave_type in self.deduct_vars:
                self.deduct_vars[leave_type].set(leave_type in deduct_types)

        # 加班工资
        overtime_pay = self.config_manager.get('overtime_pay', {})
        self.salary_enabled.set(overtime_pay.get('enabled', False))
        self.hourly_wage.insert(0, str(overtime_pay.get('hourly_wage', 50.0)))
        self.salary_weekday.insert(0, str(overtime_pay.get('weekday_rate', 1.0)))
        self.salary_weekend.insert(0, str(overtime_pay.get('weekend_rate', 1.5)))
        self.salary_holiday.insert(0, str(overtime_pay.get('holiday_rate', 2.0)))
        self.toggle_salary_inputs()

        # 节假日数据源
        use_builtin = self.config_manager.get('use_builtin_holiday', False)
        self.holiday_source.set('builtin' if use_builtin else 'chinese')
        self.update_holiday_status()

        # Web服务
        self.web_port.insert(0, str(self.config_manager.get('web_port', 8080)))

        # Webhook配置
        webhook = self.config_manager.get('webhook', {})
        self.webhook_url.insert(0, webhook.get('url', ''))
        self.webhook_enabled.set(webhook.get('enabled', False))
        self.webhook_timeout.insert(0, str(webhook.get('timeout', 10)))
        self.webhook_retry.insert(0, str(webhook.get('retry', 3)))
        self.webhook_mode.set(webhook.get('sync_mode', 'sync'))

        # 平台选择
        platform = webhook.get('platform', 'feishu')
        platform_map = {
            'feishu': '飞书 (Feishu) - 企业级协作平台',
            'dingtalk': '钉钉 (DingTalk) - 阿里云办公平台',
            'wechat': '企业微信 (WeChat Work) - 腾讯企业办公',
            'lark': 'Lark (飞书国际版) - 字节跳动国际版',
            'slack': 'Slack - 国际团队协作',
            'custom': '自定义 (Custom) - 任意Webhook服务'
        }
        self.webhook_platform.set(platform_map.get(platform, '飞书 (Feishu) - 企业级协作平台'))

        # 延迟调用
        self.dialog.after(100, lambda: self.on_platform_change(None))

    def update_holiday_status(self):
        """更新节假日状态显示"""
        if not hasattr(self, 'holiday_status') or not hasattr(self, 'holiday_source'):
            return

        use_builtin = self.holiday_source.get() == 'builtin'

        if use_builtin:
            json_path = os.path.join("modules", "holiday.json")
            if os.path.exists(json_path):
                self.holiday_status.config(text="✓ 内置数据已配置 (holiday.json)", fg="#4CAF50")
            else:
                self.holiday_status.config(text="⚠ holiday.json不存在，请点击获取第三方Api信息", fg="#F44336")
        else:
            try:
                import chinese_calendar
                self.holiday_status.config(text="✓ chinese_calendar已安装", fg="#4CAF50")
            except ImportError:
                self.holiday_status.config(text="⚠ chinese_calendar未安装", fg="#F44336")

    def toggle_salary_inputs(self):
        enabled = self.salary_enabled.get()
        state = 'normal' if enabled else 'disabled'
        self.hourly_wage.config(state=state)
        self.salary_weekday.config(state=state)
        self.salary_weekend.config(state=state)
        self.salary_holiday.config(state=state)

    def load_current_leave_types(self):
        leave_types = self.config_manager.get('leave_types', ['事假', '病假', '年假', '婚假', '产假'])
        self.leave_types_text.delete('1.0', tk.END)
        self.leave_types_text.insert('1.0', '\n'.join(leave_types))

        deduct_types = self.config_manager.get('overtime_pay.deduct_types', ['事假'])

        for widget in self.deduct_vars.values():
            try:
                widget._root().destroy()
            except:
                pass
        self.deduct_vars = {}

        deduct_frame = self.leave_frame.winfo_children()[2]
        for widget in deduct_frame.winfo_children():
            widget.destroy()

        for leave_type in leave_types:
            var = tk.BooleanVar()
            self.deduct_vars[leave_type] = var
            var.set(leave_type in deduct_types)
            cb = tk.Checkbutton(deduct_frame, text=leave_type, variable=var)
            cb.pack(side='left', padx=5, pady=2)

    def get_official_json(self):
        """获取第三方JSON数据"""
        import webbrowser
        from tkinter import simpledialog

        # 打开网页
        if messagebox.askyesno("访问网址", "将打开 https://www.mxnzp.com/doc/detail?id=1\n\n是否继续？"):
            try:
                webbrowser.open("https://www.mxnzp.com/doc/detail?id=1")
            except:
                messagebox.showinfo("提示", "无法自动打开浏览器，请手动访问:\nhttps://www.mxnzp.com/doc/detail?id=1")

        # 提示用户粘贴数据
        def import_json():
            data = simpledialog.askstring("导入JSON", "请粘贴从第三方API获取的完整JSON数据:")
            if data and data.strip():
                try:
                    # 尝试解析JSON
                    import json
                    parsed = json.loads(data)

                    # 保存到文件
                    json_path = os.path.join("modules", "holiday.json")
                    os.makedirs("modules", exist_ok=True)

                    # 支持API格式
                    if isinstance(parsed, list):
                        holiday_data = parsed
                    elif isinstance(parsed, dict) and "data" in parsed:
                        holiday_data = parsed["data"]
                    elif isinstance(parsed, dict) and any("days" in v for v in parsed.values()):
                        holiday_data = parsed
                    else:
                        raise ValueError("不支持的JSON格式")

                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(holiday_data, f, ensure_ascii=False, indent=2)

                    messagebox.showinfo("成功", f"✅ JSON数据已保存\n\n路径: {json_path}\n\n现在可以选择'内置数据'使用")
                    self.update_holiday_status()
                except Exception as e:
                    messagebox.showerror("错误", f"JSON格式错误: {str(e)}")

        # 延迟显示输入对话框
        self.dialog.after(500, import_json)

    def save_and_close(self):
        try:
            # 基础设置
            self.config_manager.set('last_user', self.basic_user.get().strip())
            self.config_manager.set('default_hours', self.basic_hours.get().strip())
            self.config_manager.set('page_size', int(self.basic_page_size.get()))

            # 请假类型
            leave_types_text = self.leave_types_text.get('1.0', tk.END).strip()
            leave_types = [t.strip() for t in leave_types_text.split('\n') if t.strip()]
            if leave_types:
                self.config_manager.set('leave_types', leave_types)

            # 扣除规则
            deduct_types = [lt for lt, var in self.deduct_vars.items() if var.get()]
            self.config_manager.set('overtime_pay.deduct_types', deduct_types)

            # 加班工资
            overtime_pay = {
                'enabled': self.salary_enabled.get(),
                'hourly_wage': float(self.hourly_wage.get() or 50.0),
                'weekday_rate': float(self.salary_weekday.get() or 1.0),
                'weekend_rate': float(self.salary_weekend.get() or 1.5),
                'holiday_rate': float(self.salary_holiday.get() or 2.0),
                'deduct_types': deduct_types
            }
            self.config_manager.set('overtime_pay', overtime_pay)

            # 节假日数据源
            use_builtin = self.holiday_source.get() == 'builtin'
            self.config_manager.set('use_builtin_holiday', use_builtin)

            # Web服务
            self.config_manager.set('web_port', int(self.web_port.get()))

            # Webhook配置
            platform_text = self.webhook_platform.get()
            platform_map = {
                '飞书 (Feishu)': 'feishu', '钉钉 (DingTalk)': 'dingtalk',
                '企业微信 (WeChat Work)': 'wechat', 'Lark (飞书国际版)': 'lark',
                'Slack': 'slack', '自定义 (Custom)': 'custom'
            }
            platform_key = platform_map.get(platform_text.split(' - ')[0] if ' - ' in platform_text else platform_text, 'feishu')

            webhook = {
                'enabled': self.webhook_enabled.get(),
                'url': self.webhook_url.get().strip(),
                'platform': platform_key,
                'headers': self.config_manager.get('webhook.headers', '{}'),
                'timeout': int(self.webhook_timeout.get()),
                'retry': int(self.webhook_retry.get()),
                'sync_mode': self.webhook_mode.get()
            }
            self.config_manager.set('webhook', webhook)

            if self.config_manager.save_config():
                messagebox.showinfo("成功", "配置已保存并生效")
                if self.on_save_callback:
                    self.on_save_callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "配置保存失败")

        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数值: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def reset_to_default(self):
        if messagebox.askyesno("确认", "确定要重置所有配置为默认值吗？\n此操作不可撤销。"):
            if self.config_manager.reset_to_default():
                messagebox.showinfo("成功", "配置已重置，请重新加载配置")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "重置失败")

    def test_webhook(self):
        """测试Webhook连接"""
        if not self.webhook_enabled.get():
            messagebox.showwarning("警告", "请先启用Webhook")
            return

        url = self.webhook_url.get().strip()
        if not url:
            messagebox.showwarning("警告", "请先配置Webhook URL")
            return

        from modules.webhook import WebhookModule
        from core.config import ConfigManager

        # 创建临时配置
        temp_config = self.config_manager.config.copy()

        platform_text = self.webhook_platform.get()
        platform_map = {
            '飞书 (Feishu)': 'feishu', '钉钉 (DingTalk)': 'dingtalk',
            '企业微信 (WeChat Work)': 'wechat', 'Lark (飞书国际版)': 'lark',
            'Slack': 'slack', '自定义 (Custom)': 'custom'
        }
        platform_key = platform_map.get(platform_text.split(' - ')[0] if ' - ' in platform_text else platform_text, 'feishu')

        temp_config['webhook'] = {
            'enabled': True,
            'url': url,
            'platform': platform_key,
            'timeout': int(self.webhook_timeout.get()),
            'retry': int(self.webhook_retry.get()),
            'headers': '{}',
            'sync_mode': self.webhook_mode.get()
        }

        temp_manager = ConfigManager()
        temp_manager.config = temp_config

        webhook_module = WebhookModule(temp_manager)
        result = webhook_module.test()

        # 修复返回值处理
        if isinstance(result, dict):
            if result.get('status') == 'success':
                messagebox.showinfo("测试成功",
                                   f"✅ {result.get('message', '成功')}\n\n"
                                   f"平台: {result.get('platform', 'N/A')}\n"
                                   f"状态码: {result.get('code', 'N/A')}")
            else:
                messagebox.showerror("测试失败", f"❌ {result.get('message', '未知错误')}")
        elif isinstance(result, tuple) and len(result) == 2:
            success, message = result
            if success:
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("失败", message)
        else:
            if result:
                messagebox.showinfo("成功", "Webhook测试成功")
            else:
                messagebox.showerror("失败", "Webhook测试失败")

    def install_chinesecalendar(self):
        """安装chinesecalendar"""
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", "chinesecalendar"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("成功", "chinesecalendar安装成功！\n\n请重启程序")
            else:
                messagebox.showerror("失败", f"安装失败:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("错误", f"安装过程中出错: {str(e)}")

    def install_openpyxl(self):
        """安装openpyxl"""
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("成功", "openpyxl安装成功！\n\n现在可以导出Excel")
            else:
                messagebox.showerror("失败", f"安装失败:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("错误", f"安装过程中出错: {str(e)}")
