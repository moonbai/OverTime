# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core.utils import validate_date, format_timestamp, get_web_service_url

class MainWindow:
    """主程序界面 - 优化布局"""

    def __init__(self, root, config_manager, data_manager, modules,
                 open_settings_callback, start_web_callback, stop_web_callback):
        self.root = root
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.modules = modules
        self.open_settings_callback = open_settings_callback
        self.start_web_callback = start_web_callback
        self.stop_web_callback = stop_web_callback

        # 分页状态
        self.current_page = 1
        self.total_pages = 1
        self.current_filter = {}

        # 创建界面
        self.create_widgets()

        # 延迟初始化
        self.root.after(100, self.update_summary)
        self.root.after(200, self.refresh_records)
        self.root.after(300, self._force_set_today)

    def create_widgets(self):
        """创建界面组件 -标签页布局"""
        # 顶部工具栏
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill='x', padx=10, pady=5)

        # 操作按钮组
        btn_frame = tk.Frame(toolbar)
        btn_frame.pack(side='left', fill='x', expand=True)

        tk.Button(btn_frame, text="⚙️ 设置", command=self.open_settings_callback,
                 bg="#607D8B", fg="white", width=10).pack(side='left', padx=3)

        tk.Button(btn_frame, text="📂 导入", command=self.import_records,
                 bg="#FF9800", fg="white", width=10).pack(side='left', padx=3)

        tk.Button(btn_frame, text="📊 导出", command=self.export_to_excel,
                 bg="#2196F3", fg="white", width=10).pack(side='left', padx=3)

        tk.Button(btn_frame, text="📋 全部", command=self.view_all_records,
                 bg="#9C27B0", fg="white", width=10).pack(side='left', padx=3)

        # Web服务按钮组
        web_frame = tk.Frame(toolbar)
        web_frame.pack(side='right')

        self.web_status_label = tk.Label(web_frame, text="Web: 未启动",
                                        font=("Arial", 8), fg="#666666")
        self.web_status_label.pack(side='left', padx=(0, 5))

        tk.Button(web_frame, text="▶️ 启动", command=self.start_web_callback,
                 bg="#4CAF50", fg="white", width=8).pack(side='left', padx=2)

        tk.Button(web_frame, text="⏹️ 停止", command=self.stop_web_callback,
                 bg="#F44336", fg="white", width=8).pack(side='left', padx=2)

        # 主内容区域 - 标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # 标签页1: 数据录入
        tab_input = ttk.Frame(notebook)
        notebook.add(tab_input, text="📝 数据录入")
        self.create_input_tab(tab_input)

        # 标签页2: 汇总统计
        tab_summary = ttk.Frame(notebook)
        notebook.add(tab_summary, text="📊 汇总统计")
        self.create_summary_tab(tab_summary)

        # 标签页3: 数据筛选
        tab_filter = ttk.Frame(notebook)
        notebook.add(tab_filter, text="🔍 数据筛选")
        self.create_filter_tab(tab_filter)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             relief=tk.SUNKEN, anchor='w', font=("Arial", 8))
        status_bar.pack(side='bottom', fill='x', padx=10, pady=2)

    def create_input_tab(self, parent):
        """数据录入标签页 - 优化布局"""
        # 节假日提示
        holiday_frame = tk.LabelFrame(parent, text="节假日判断", font=("Arial", 9, "bold"), padx=5, pady=3)
        holiday_frame.pack(fill='x', pady=(0, 5))

        self.holiday_info = tk.Label(holiday_frame, text="", font=("Arial", 8))
        self.holiday_info.pack(anchor='w', padx=5)
        self.update_holiday_info()

        # 录入表单
        form_frame = tk.LabelFrame(parent, text="填写表单", font=("Arial", 9, "bold"), padx=5, pady=5)
        form_frame.pack(fill='x', pady=(0, 5), expand=False)

        # 用户和日期在同一行
        row1 = tk.Frame(form_frame)
        row1.pack(fill='x', pady=3)

        tk.Label(row1, text="用户:*", width=6, anchor='w').pack(side='left')
        self.user_entry = tk.Entry(row1, width=12)
        self.user_entry.pack(side='left', padx=2)

        # 立即读取默认用户
        default_user = self.config_manager.get('last_user', '')
        if default_user:
            self.user_entry.insert(0, default_user)

        tk.Label(row1, text="日期:*", width=6, anchor='w').pack(side='left', padx=(10, 0))
        self.date_display = tk.Entry(row1, width=12, state='readonly', readonlybackground='white')
        self.date_display.pack(side='left', padx=2)

        tk.Button(row1, text="📅", command=self.open_calendar,
                 bg="#2196F3", fg="white", width=2).pack(side='left', padx=2)

        self.date_entry = tk.Entry(row1, width=12)
        self.date_entry.pack_forget()

        self.result_label = tk.Label(row1, text="等待日期...", font=("Arial", 8), fg="#666666")
        self.result_label.pack(side='left', padx=5)

        # 绑定事件
        self.date_display.bind('<FocusOut>', lambda e: self.update_date_and_detect())
        self.date_display.bind('<Return>', lambda e: self.update_date_and_detect())

        # 日期类型 - 紧凑布局
        row2 = tk.Frame(form_frame)
        row2.pack(fill='x', pady=3)
        tk.Label(row2, text="类型:*", width=6, anchor='w').pack(side='left')
        self.day_type = tk.StringVar()
        day_types = [("工作日", "工作日"), ("休息日", "休息日"), ("节假日", "节假日"), ("调休日", "调休日")]
        for i, (text, value) in enumerate(day_types):
            rb = tk.Radiobutton(row2, text=text, variable=self.day_type, value=value)
            rb.pack(side='left', padx=4)
            if i == 0:
                rb.select()

        # 操作选择
        row3 = tk.Frame(form_frame)
        row3.pack(fill='x', pady=3)
        tk.Label(row3, text="操作:*", width=6, anchor='w').pack(side='left')
        self.is_leave = tk.BooleanVar()
        self.is_leave.set(False)
        tk.Checkbutton(row3, text="请假", variable=self.is_leave,
                      command=self.toggle_leave_options).pack(side='left', padx=(0, 10))

        # 动态区域
        self.dynamic_frame = tk.Frame(row3)
        self.dynamic_frame.pack(side='left')

        # 加班时长
        self.work_frame = tk.Frame(self.dynamic_frame)
        tk.Label(self.work_frame, text="加班:", width=4, anchor='w').pack(side='left')
        self.work_hours = tk.Entry(self.work_frame, width=6)
        self.work_hours.pack(side='left', padx=2)
        self.work_hours.insert(0, self.config_manager.get('default_hours', '8'))
        tk.Label(self.work_frame, text="小时", font=("Arial", 8)).pack(side='left')
        self.work_frame.pack(side='left')

        # 请假选项（初始隐藏）
        self.leave_frame = tk.Frame(self.dynamic_frame)
        self.leave_dropdown = None
        self.leave_hours_var = None

        # 提交按钮
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="✅ 提交记录", command=self.submit_record,
                 bg="#4CAF50", fg="white", width=15, font=("Arial", 9, "bold")).pack(side='left', padx=3)

        # 延迟设置日期
        self.root.after(100, self._force_set_today)

    def _force_set_today(self):
        """强制设置今天日期"""
        try:
            if hasattr(self, 'date_display') and hasattr(self, 'date_entry'):
                today = datetime.now().strftime("%Y-%m-%d")

                self.date_display.config(state='normal')
                self.date_display.delete(0, tk.END)
                self.date_display.insert(0, today)
                self.date_display.config(state='readonly')

                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, today)

                if hasattr(self, 'auto_detect_day_type'):
                    self.auto_detect_day_type()

                print(f"✅ 已自动设置日期: {today}")
        except Exception as e:
            print(f"⚠️ 设置日期失败: {e}")

    def create_summary_tab(self, parent):
        """汇总统计标签页"""
        self.summary_content = tk.Frame(parent, relief=tk.RIDGE, borderwidth=1, bg="#f5f5f5")
        self.summary_content.pack(fill='both', expand=True, padx=5, pady=5)

        # 立即刷新按钮
        refresh_btn = tk.Button(parent, text="🔄 刷新汇总", command=self.update_summary,
                               bg="#009688", fg="white", width=15)
        refresh_btn.pack(pady=5)

    def create_filter_tab(self, parent):
        """数据筛选标签页"""
        # 筛选条件
        filter_frame = tk.LabelFrame(parent, text="筛选条件", font=("Arial", 9, "bold"), padx=10, pady=10)
        filter_frame.pack(fill='x', pady=(0, 10))

        # 用户
        row1 = tk.Frame(filter_frame)
        row1.pack(fill='x', pady=5)
        tk.Label(row1, text="用户:", width=8, anchor='w').pack(side='left')
        self.filter_user = tk.Entry(row1, width=15)
        self.filter_user.pack(side='left', padx=5)

        # 日期范围
        row2 = tk.Frame(filter_frame)
        row2.pack(fill='x', pady=5)
        tk.Label(row2, text="日期:", width=8, anchor='w').pack(side='left')
        self.filter_date_start = tk.Entry(row2, width=12)
        self.filter_date_start.pack(side='left', padx=5)
        tk.Label(row2, text="至").pack(side='left', padx=5)
        self.filter_date_end = tk.Entry(row2, width=12)
        self.filter_date_end.pack(side='left', padx=5)

        # 类型
        row3 = tk.Frame(filter_frame)
        row3.pack(fill='x', pady=5)
        tk.Label(row3, text="类型:", width=8, anchor='w').pack(side='left')
        self.filter_type = ttk.Combobox(row3, values=["所有", "工作日", "休息日", "节假日", "调休日"],
                                       width=12, state="readonly")
        self.filter_type.pack(side='left', padx=5)
        self.filter_type.set("所有")

        # 按钮
        btn_frame = tk.Frame(filter_frame)
        btn_frame.pack(fill='x', pady=10)
        tk.Button(btn_frame, text="🔍 筛选", command=self.apply_filter,
                 bg="#009688", fg="white", width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🔄 清空", command=self.clear_filter,
                 bg="#795548", fg="white", width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="📋 刷新记录", command=self.refresh_records,
                 bg="#4CAF50", fg="white", width=12).pack(side='left', padx=5)

        # 分页控制
        pagination_frame = tk.Frame(parent)
        pagination_frame.pack(fill='x', pady=5)

        tk.Button(pagination_frame, text="上一页", command=self.prev_page,
                 bg="#E0E0E0", width=8).pack(side='left', padx=5)

        tk.Button(pagination_frame, text="下一页", command=self.next_page,
                 bg="#E0E0E0", width=8).pack(side='left', padx=5)

        self.page_label = tk.Label(pagination_frame, text="第 1 页", font=("Arial", 9, "bold"))
        self.page_label.pack(side='left', padx=10)

        tk.Label(pagination_frame, text="每页:").pack(side='left', padx=(10, 0))
        self.page_size_var = tk.StringVar(value=str(self.config_manager.get('page_size', 10)))
        page_size_spin = tk.Spinbox(pagination_frame, from_=5, to=50, width=4,
                                   textvariable=self.page_size_var, command=self.change_page_size)
        page_size_spin.pack(side='left', padx=5)

        # 记录显示
        record_frame = tk.LabelFrame(parent, text="记录列表", font=("Arial", 9, "bold"), padx=10, pady=10)
        record_frame.pack(fill='both', expand=True)
        self.record_frame = tk.Frame(record_frame)
        self.record_frame.pack(fill='both', expand=True)

    def update_holiday_info(self):
        """更新节假日信息显示"""
        if hasattr(self, 'config_manager'):
            use_builtin = self.config_manager.get('use_builtin_holiday', False)
            years = self.modules['holiday'].get_supported_years()

            if use_builtin:
                self.holiday_info.config(text=f"✓内置数据 | 支持年份: {years[0]}-{years[-1]}", fg="#4CAF50")
            else:
                if self.modules['holiday'].calendar_available:
                    self.holiday_info.config(text=f"✓ chinese_calendar | 支持年份: {years[0]}-{years[-1]}", fg="#4CAF50")
                else:
                    self.holiday_info.config(text=f"⚠️ 未配置数据源 | 支持年份: 2024-2026", fg="#F44336")

    def toggle_leave_options(self):
        """切换请假选项"""
        try:
            if self.is_leave.get():
                # 清除旧的
                if self.leave_dropdown:
                    self.leave_dropdown.destroy()
                self.work_frame.pack_forget()

                # 创建新的
                tk.Label(self.leave_frame, text="请假类型:", width=6, anchor='w').pack(side='left')
                self.leave_type = tk.StringVar()

                leave_types = self.config_manager.get('leave_types', ['事假', '病假', '年假', '婚假', '产假'])
                self.leave_dropdown = ttk.Combobox(self.leave_frame, textvariable=self.leave_type,
                                                  values=leave_types, width=8, state="readonly")
                self.leave_dropdown.pack(side='left', padx=2)
                self.leave_dropdown.bind("<<ComboboxSelected>>", self.toggle_leave_hours)

                # 请假时长
                self.leave_hour_frame = tk.Frame(self.leave_frame)
                self.leave_hours_var = tk.StringVar()
                leave_hours = [("半天(-4)", "-4"), ("全天(-8)", "-8")]
                for text, value in leave_hours:
                    rb = tk.Radiobutton(self.leave_hour_frame, text=text,
                                       variable=self.leave_hours_var, value=value)
                    rb.pack(side='left', padx=3)

                self.leave_frame.pack(side='left')
            else:
                self.leave_frame.pack_forget()
                self.work_frame.pack(side='left')
        except Exception as e:
            print(f"⚠ 切换请假界面错误: {e}")

    def toggle_leave_hours(self, event=None):
        """仅在选择事假时显示时长选项"""
        try:
            if self.leave_type.get() == "事假":
                self.leave_hour_frame.pack(side='left', padx=5)
            else:
                self.leave_hour_frame.pack_forget()
        except:
            pass

    def open_calendar(self):
        """打开日历选择器 - 优化版"""
        try:
            from tkcalendar import Calendar
            from datetime import datetime

            # 创建弹出窗口
            cal_window = tk.Toplevel(self.root)
            cal_window.title("选择日期")
            cal_window.geometry("320x350")
            cal_window.transient(self.root)
            cal_window.grab_set()

            # 居中显示
            self.root.update_idletasks()
            root_x = self.root.winfo_x()
            root_y = self.root.winfo_y()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()

            cal_w = 320
            cal_h = 350

            x = root_x + (root_w - cal_w) // 2
            y = root_y + (root_h - cal_h) // 2

            cal_window.geometry(f"{cal_w}x{cal_h}+{x}+{y}")

            # 确定初始日期
            try:
                existing_date = self.date_entry.get().strip()
                if existing_date:
                    initial_date = datetime.strptime(existing_date, "%Y-%m-%d")
                else:
                    initial_date = datetime.now()
            except:
                initial_date = datetime.now()

            # 创建日历
            cal = Calendar(cal_window,
                          selectmode='day',
                          year=initial_date.year,
                          month=initial_date.month,
                          day=initial_date.day,
                          date_pattern='yyyy-mm-dd')
            cal.pack(padx=10, pady=10)

            # 按钮区域
            btn_frame = tk.Frame(cal_window)
            btn_frame.pack(pady=5)

            def select_date():
                selected = cal.get_date()

                self.date_display.config(state='normal')
                self.date_display.delete(0, tk.END)
                self.date_display.insert(0, selected)
                self.date_display.config(state='readonly')

                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, selected)

                cal_window.destroy()
                self.auto_detect_day_type()

            def go_today():
                today = datetime.now()
                cal.selection_set(today)
                cal.display_date(today)

            tk.Button(btn_frame, text="✅确定", command=select_date,
                     bg="#4CAF50", fg="white", width=8).pack(side='left', padx=3)

            tk.Button(btn_frame, text="📅今天", command=go_today,
                     bg="#2196F3", fg="white", width=8).pack(side='left', padx=3)

            tk.Button(btn_frame, text="✖取消", command=cal_window.destroy,
                     bg="#E0E0E0", width=8).pack(side='left', padx=3)

        except ImportError:
            messagebox.showinfo("提示", "未安装tkcalendar库\n\n请执行安装：\npip install tkcalendar\n\n或直接手动输入日期（格式：YYYY-MM-DD）")
        except Exception as e:
            messagebox.showerror("错误", f"打开日历失败: {str(e)}")

    def update_date_and_detect(self):
        """更新日期并自动检测（支持手动输入）"""
        date_str = self.date_display.get().strip()
        if date_str:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, date_str)
            self.auto_detect_day_type()

    def auto_detect_day_type(self):
        """自动判断日期类型 - 显示详细信息"""
        try:
            date_str = self.date_entry.get().strip()
            if not date_str:
                self.result_label.config(text="等待输入日期...", fg="#666666")
                return
    
            datetime.strptime(date_str, "%Y-%m-%d")
    
            # 使用get_holiday_info获取详细信息
            info = self.modules['holiday'].get_holiday_info(date_str)
    
            # 打印详细信息
            print(f"\n{'='*60}")
            print(f"📅 日期检测: {date_str}")
            print(f"{'='*60}")
            print(f"类型: {info['type']}")
            print(f"描述: {info['typeDes']}")
            print(f"详情类型: {info['detailsType']}")
            print(f"工作日序号: {info['indexWorkDayOfMonth']}")
    
            # 🎯 根据detailsType返回最终类型
            if info['detailsType'] == 3:
                final_type = "节假日"
                reason = f"{info['typeDes']}(三倍工资)"
            elif info['detailsType'] == 2:
                final_type = "休息日"  # ✅ 普通节假日 = 休息日
                reason = f"{info['typeDes']}(普通节假日)"
            elif info['detailsType'] == 1:
                final_type = "休息日"
                reason = info['typeDes']
            elif info['detailsType'] == 0:
                final_type = "工作日"
                reason = info['typeDes']
            else:
                final_type = "未知"
                reason = "未知"
    
            print(f"最终判定: {final_type} ({reason})")
            print(f"{'='*60}\n")
    
            # 更新界面
            self.day_type.set(final_type)
            self.result_label.config(text=f"✓ {final_type} ({reason})", fg="#4CAF50")
    
            self.root.after(3000, lambda: self.result_label.config(fg="#666666"))
            self.status_var.set(f"已自动判断: {final_type} ({reason})")
    
        except ValueError:
            self.result_label.config(text="❌ 日期格式错误", fg="#F44336")
            self.root.after(3000, lambda: self.result_label.config(text="等待输入日期...", fg="#666666"))
        except Exception as e:
            self.result_label.config(text=f"❌ 检测失败", fg="#F44336")
            print(f"\n❌ 检测失败: {e}\n")
            self.root.after(3000, lambda: self.result_label.config(text="等待输入日期...", fg="#666666"))
    
    def submit_record(self):
        """提交记录"""
        try:
            user = self.user_entry.get().strip()
            date_str = self.date_entry.get().strip()
            day_type = self.day_type.get()

            if not user or not date_str:
                messagebox.showerror("错误", "请填写用户和日期")
                return

            if not validate_date(date_str):
                messagebox.showerror("错误", "日期格式错误，请使用YYYY-MM-DD")
                return

            # 打印提交信息
            print(f"\n{'='*60}")
            print(f"📝 提交记录")
            print(f"{'='*60}")
            print(f"用户: {user}")
            print(f"日期: {date_str}")
            print(f"类型: {day_type}")

            # 验证类型
            if self.modules['holiday']:
                detected_type, reason = self.modules['holiday'].get_day_type(date_str)
                print(f"检测类型: {detected_type} ({reason})")

                if detected_type != day_type and not self.is_leave.get():
                    print(f"⚠️ 类型不匹配！检测到 {detected_type}，但用户选择 {day_type}")
                    if not messagebox.askyesno("类型不匹配",
                        f"检测到 {detected_type} ({reason})\n但你选择的是 {day_type}\n\n确定要提交吗？"):
                        print(f"❌ 用户取消提交\n")
                        return

            # 准备数据
            data = {
                'user': user,
                'date': date_str,
                'day_type': day_type,
                'is_leave': self.is_leave.get(),
                'calculate_salary': self.config_manager.get('overtime_pay.enabled', False),
                'submit_method': '程序'
            }

            if self.is_leave.get():
                leave_type = self.leave_type.get()
                if not leave_type:
                    messagebox.showerror("错误", "请选择请假类型")
                    return

                deduct_types = self.config_manager.get('overtime_pay.deduct_types', ['事假'])
                should_deduct = leave_type in deduct_types

                if leave_type == "事假":
                    if not self.leave_hours_var.get():
                        messagebox.showerror("错误", "事假必须选择时长")
                        return
                    data['leave_type'] = leave_type
                    data['leave_hours'] = self.leave_hours_var.get()
                else:
                    data['leave_type'] = leave_type
                    data['leave_hours'] = '0'

                if should_deduct:
                    data['day_type'] = "休息日"
                    data['work_hours'] = data.get('leave_hours', '0')
                else:
                    data['work_hours'] = "0"
            else:
                work_hours = self.work_hours.get().strip()
                if not work_hours:
                    messagebox.showerror("错误", "请填写加班时长")
                    return

                try:
                    hours = float(work_hours)
                    if hours < 0:
                        messagebox.showerror("错误", "加班时长不能为负数")
                        return
                    if hours > 24 and not messagebox.askyesno("警告", f"加班时长超过24小时: {hours}\n确定提交吗？"):
                        return
                except:
                    messagebox.showerror("错误", "加班时长必须是数字")
                    return

                data['work_hours'] = work_hours

            # 计算工资
            if data['calculate_salary']:
                if data['is_leave']:
                    should_deduct = data['leave_type'] in self.config_manager.get('overtime_pay.deduct_types', ['事假'])
                    if should_deduct:
                        data['salary'] = self.modules['salary'].calculate(data['date'], data.get('leave_hours', '0'), data['day_type'])
                    else:
                        data['salary'] = "0"
                else:
                    data['salary'] = self.modules['salary'].calculate(data['date'], data.get('work_hours', '0'), data['day_type'])
            else:
                data['salary'] = "0"

            # 提交
            success, message, record = self.modules['overtime'].submit_overtime(data)

            if success:
                # Webhook同步
                if self.config_manager.get('webhook.enabled', False):
                    webhook_data = {
                        '类型': '桌面程序填报',
                        '日期': data['date'],
                        '用户': data['user'],
                        '工作类型': data['day_type'],
                        '工作时长': data.get('work_hours', data.get('leave_hours', '0')),
                        '请假类型': data.get('leave_type', '无'),
                        '请假时长': data.get('leave_hours', '无'),
                        '提交时间': format_timestamp(),
                        '工资': data['salary'],
                        '提交方式': '程序'
                    }
                    self.modules['webhook'].send(webhook_data)

                print(f"✅ 提交成功！工资: {data['salary']}")
                print(f"{'='*60}\n")

                messagebox.showinfo("成功", f"{message}\n工资: {data['salary']}")
                self.status_var.set(f"✓ 已提交 - {user}")
                self.root.after(3000, lambda: self.status_var.set("就绪"))

                # 清空和刷新
                self.user_entry.delete(0, tk.END)
                default_user = self.config_manager.get('last_user', '')
                if default_user:
                    self.user_entry.insert(0, default_user)

                self.refresh_records()
                self.update_summary()
            else:
                messagebox.showerror("失败", message)
                print(f"❌ 提交失败: {message}\n")
        except Exception as e:
            messagebox.showerror("错误", f"提交失败: {str(e)}")
            print(f"❌ 提交异常: {e}\n")

    def apply_filter(self):
        """应用筛选"""
        self.current_filter = {}

        user = self.filter_user.get().strip()
        if user:
            self.current_filter['user'] = user

        date_start = self.filter_date_start.get().strip()
        date_end = self.filter_date_end.get().strip()
        if date_start and validate_date(date_start):
            self.current_filter['date_start'] = date_start
        if date_end and validate_date(date_end):
            self.current_filter['date_end'] = date_end

        filter_type = self.filter_type.get()
        if filter_type != "所有":
            self.current_filter['type'] = filter_type

        self.current_page = 1
        self.refresh_records()
        self.status_var.set(f"筛选已应用 - {len(self.current_filter)} 个条件")

    def clear_filter(self):
        """清空筛选"""
        self.filter_user.delete(0, tk.END)
        self.filter_date_start.delete(0, tk.END)
        self.filter_date_end.delete(0, tk.END)
        self.filter_type.set("所有")
        self.current_filter = {}
        self.current_page = 1
        self.refresh_records()
        self.status_var.set("筛选已清空")

    def refresh_records(self):
        """刷新记录显示"""
        try:
            for widget in self.record_frame.winfo_children():
                widget.destroy()

            all_records, total_count = self.data_manager.get_filtered_records(self.current_filter)

            if total_count == 0:
                tk.Label(self.record_frame, text="暂无记录", font=("Arial", 10),
                        bg="white", pady=20).pack(fill='x')
                self.page_label.config(text="第 0/0 页")
                return

            page_size = int(self.page_size_var.get())
            self.total_pages = (total_count + page_size - 1) // page_size

            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            if self.current_page < 1:
                self.current_page = 1

            start_idx = (self.current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_count)

            page_records = all_records[start_idx:end_idx]

            headers = ["日期", "用户", "类型", "工时", "请假类型", "请假时长", "工资", "提交时间"]
            for i, header in enumerate(headers):
                tk.Label(self.record_frame, text=header, font=("Arial", 9, "bold"),
                        relief=tk.RIDGE, width=11, bg="#e0e0e0").grid(row=0, column=i, sticky="nsew")

            for i, record in enumerate(page_records):
                for j, item in enumerate(record[:8]):
                    tk.Label(self.record_frame, text=item, relief=tk.RIDGE,
                            width=11, bg="white", font=("Arial", 8)).grid(row=i+1, column=j, sticky="nsew")

            self.page_label.config(text=f"第 {self.current_page}/{self.total_pages} 页")
            self.status_var.set(f"显示 {start_idx+1}-{end_idx} 条，共 {total_count} 条记录")

        except Exception as e:
            print(f"✗ 刷新记录失败: {e}")
            tk.Label(self.record_frame, text=f"加载失败: {str(e)}", bg="white").grid(row=1, column=0, columnspan=8)

    def update_summary(self):
        """更新汇总统计"""
        try:
            for widget in self.summary_content.winfo_children():
                widget.destroy()

            summary = self.modules['overtime'].get_monthly_summary()
            if summary.get('empty', True):
                tk.Label(self.summary_content, text=f"{summary['month']} 月暂无记录",
                        font=("Arial", 9), bg="#f5f5f5", fg="#666666").pack(pady=20, padx=10, anchor='w')
                return

            # 汇总标题
            title_frame = tk.Frame(self.summary_content, bg="#e3f2fd")
            title_frame.pack(fill='x', padx=10, pady=5)
            tk.Label(title_frame, text=f"【{summary['month']} 月汇总】",
                    font=("Arial", 10, "bold"), bg="#e3f2fd", fg="#1976D2").pack(anchor='w')

            # 基础统计
            base_frame = tk.Frame(self.summary_content, bg="#f5f5f5")
            base_frame.pack(fill='x', padx=10, pady=3)
            total_hours = summary['total_hours']
            tk.Label(base_frame, text=f"总时长: {total_hours:.1f}小时",
                    bg="#f5f5f5", font=("Arial", 9)).pack(side='left', padx=5)

            # 工资统计
            if self.config_manager.get('overtime_pay.enabled', False):
                total_salary, _ = self.modules['salary'].calculate_batch(self.data_manager.get_monthly_records(summary['month']))
                if total_salary > 0:
                    hourly_wage = self.config_manager.get('overtime_pay.hourly_wage', 50.0)
                    tk.Label(base_frame, text=f"小时工资: {hourly_wage}元/小时",
                            bg="#f5f5f5", font=("Arial", 9)).pack(side='left', padx=10)
                    tk.Label(base_frame, text=f"总工资: {total_salary:.2f}元",
                            bg="#f5f5f5", font=("Arial", 9, "bold"), fg="#4CAF50").pack(side='left', padx=10)

            # 详细分类
            for day_type, data in summary['details'].items():
                if data['hours'] > 0:
                    detail_frame = tk.Frame(self.summary_content, bg="#f5f5f5")
                    detail_frame.pack(fill='x', padx=10, pady=2)
                    text = f"  {day_type}: {data['hours']:.1f}小时"
                    tk.Label(detail_frame, text=text, bg="#f5f5f5", font=("Arial", 9)).pack(anchor='w')

        except Exception as e:
            print(f"✗ 更新汇总错误: {e}")
            tk.Label(self.summary_content, text=f"汇总显示错误: {str(e)}",
                    font=("Arial", 8), bg="#f5f5f5", fg="#D32F2F").pack(pady=10, padx=10, anchor='w')

    def update_web_status(self, url, running):
        """更新Web服务状态"""
        if running:
            self.web_status_label.config(text=f"Web: 运行中", fg="#4CAF50")
            if hasattr(self, 'web_url_var'):
                self.web_url_var.set(url)
            self.status_var.set(f"✓ Web服务已启动: {url}")
        else:
            self.web_status_label.config(text="Web: 未启动", fg="#666666")
            if hasattr(self, 'web_url_var'):
                self.web_url_var.set("")
            self.status_var.set("Web服务已停止")

    def on_config_changed(self):
        """配置改变时的回调"""
        self.work_hours.delete(0, tk.END)
        self.work_hours.insert(0, self.config_manager.get('default_hours', '8'))

        self.page_size_var.set(str(self.config_manager.get('page_size', 10)))

        # 更新请假类型
        if self.is_leave.get():
            self.toggle_leave_options()

        # 更新节假日信息
        self.update_holiday_info()

        self.update_summary()

        self.status_var.set("配置已更新")
        self.root.after(3000, lambda: self.status_var.set("就绪"))

    def import_records(self):
        """导入记录"""
        try:
            import tkinter.filedialog as fd
            file_path = fd.askopenfilename(
                title="选择要导入的文件",
                filetypes=[("CSV文件", "*.csv"), ("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
            )

            if not file_path:
                return

            if not messagebox.askyesno("确认", f"确定要导入:\n{file_path}\n\n数据将添加到现有记录中。"):
                return

            last_user = self.config_manager.get('last_user', '未知')
            imported, failed, errors = self.data_manager.import_csv(file_path, last_user)

            result_msg = f"导入完成！\n\n成功: {imported} 条\n失败: {failed} 条"
            if errors:
                result_msg += "\n\n前5个错误:\n" + "\n".join(errors)

            messagebox.showinfo("导入结果", result_msg)

            if imported > 0:
                self.refresh_records()
                self.update_summary()
                self.status_var.set(f"成功导入 {imported} 条记录")
                self.root.after(3000, lambda: self.status_var.set("就绪"))

        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")

    def export_to_excel(self):
        """导出到Excel"""
        try:
            import tkinter.filedialog as fd
            save_path = fd.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                title="保存Excel文件",
                initialfile=f"加班记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not save_path:
                return

            if self.data_manager.export_excel(save_path):
                if messagebox.askyesno("成功", f"Excel文件已保存:\n{save_path}\n\n是否立即打开？"):
                    import os
                    os.startfile(save_path) if os.name == 'nt' else os.system(f'open "{save_path}"')
            else:
                messagebox.showerror("错误", "导出失败，请检查是否安装了openpyxl")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def view_all_records(self):
        """查看所有记录 - 表格形式"""
        try:
            top = tk.Toplevel(self.root)
            top.title("所有记录")
            top.geometry("1100x500")

            # 主框架
            main_frame = tk.Frame(top)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # 顶部按钮区域
            btn_frame = tk.Frame(main_frame)
            btn_frame.pack(fill='x', pady=5)

            tk.Button(btn_frame, text="🔄 刷新", command=lambda: load_data(True),
                     bg="#4CAF50", fg="white", width=10).pack(side='left', padx=3)

            tk.Button(btn_frame, text="📊 导出Excel", command=self.export_to_excel,
                     bg="#2196F3", fg="white", width=12).pack(side='left', padx=3)

            tk.Button(btn_frame, text="🔍筛选", command=self.open_filter_dialog,
                     bg="#FF9800", fg="white", width=10).pack(side='left', padx=3)

            tk.Button(btn_frame, text="✖ 关闭", command=top.destroy,
                     bg="#E0E0E0", width=10).pack(side='right', padx=3)

            # 表格容器
            table_frame = tk.Frame(main_frame)
            table_frame.pack(fill='both', expand=True)

            # 滚动条
            scrollbar_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

            scrollbar_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

            # 表格控件
            tree = ttk.Treeview(table_frame,
                               columns=('日期', '用户', '类型', '工作时长', '请假类型', '请假时长', '提交时间', '工资'),
                               show='headings',
                               yscrollcommand=scrollbar_y.set,
                               xscrollcommand=scrollbar_x.set)

            scrollbar_y.config(command=tree.yview)
            scrollbar_x.config(command=tree.xview)

            # 配置列
            columns = [
                ('日期', 100), ('用户', 80), ('类型', 80), ('工作时长', 70),
                ('请假类型', 80), ('请假时长', 70), ('提交时间', 130), ('工资', 80)
            ]

            for col, width in columns:
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor='center', minwidth=width)

            tree.pack(fill='both', expand=True)

            # 数据加载函数
            def load_data(refresh=False):
                # 清空现有数据
                for item in tree.get_children():
                    tree.delete(item)

                # 获取数据
                records, total = self.data_manager.get_all_records_with_total()

                if not records:
                    tree.insert('', 'end', values=('暂无数据', '', '', '', '', '', '', ''))
                    return

                # 插入数据
                for record in records:
                    tree.insert('', 'end', values=record[:8])

                # 更新状态
                if hasattr(self, 'status_var'):
                    self.status_var.set(f"共 {total} 条记录")

            #右键菜单
            def popup_menu(event):
                menu = tk.Menu(top, tearoff=0)
                menu.add_command(label="查看详情", command=lambda: show_detail())
                menu.add_command(label="删除记录", command=lambda: delete_record())
                menu.tk_popup(event.x_root, event.y_root)

            def show_detail():
                selected = tree.selection()
                if selected:
                    item = tree.item(selected[0])
                    values = item['values']
                    messagebox.showinfo("记录详情",
                                      f"日期: {values[0]}\n用户: {values[1]}\n类型: {values[2]}\n"
                                      f"时长: {values[3]}小时\n请假: {values[4]} ({values[5]})\n"
                                      f"工资: {values[7]}\n时间: {values[6]}")

            def delete_record():
                selected = tree.selection()
                if selected and messagebox.askyesno("确认", "确定要删除这条记录吗？"):
                    item = tree.item(selected[0])
                    values = item['values']
                    # 调用删除逻辑（需要在data_manager中添加）
                    tree.delete(selected[0])
                    messagebox.showinfo("成功", "记录已删除")

            tree.bind('<Button-3>', popup_menu)
            tree.bind('<Double-1>', lambda e: show_detail())

            # 初始加载
            load_data()

        except Exception as e:
            messagebox.showerror("错误", f"打开记录窗口失败: {str(e)}")

    def open_filter_dialog(self):
        """打开筛选对话框"""
        try:
            from tkinter import simpledialog

            user = simpledialog.askstring("筛选", "输入用户名称（留空不过滤）:")
            if user is None:
                return

            date_start = simpledialog.askstring("筛选", "开始日期 YYYY-MM-DD（留空不过滤）:")
            if date_start is None:
                return

            date_end = simpledialog.askstring("筛选", "结束日期 YYYY-MM-DD（留空不过滤）:")
            if date_end is None:
                return

            # 应用筛选
            self.current_filter = {}
            if user and user.strip():
                self.current_filter['user'] = user.strip()
            if date_start and validate_date(date_start):
                self.current_filter['date_start'] = date_start
            if date_end and validate_date(date_end):
                self.current_filter['date_end'] = date_end

            # 重新打开记录窗口
            self.view_all_records()

        except Exception as e:
            messagebox.showerror("错误", f"筛选出错: {str(e)}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_records()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_records()

    def change_page_size(self):
        try:
            size = int(self.page_size_var.get())
            if size < 5:
                size = 5
            elif size > 50:
                size = 50
            self.config_manager.set('page_size', size)
            self.config_manager.save_config()
            self.current_page = 1
            self.refresh_records()
        except:
            pass

    def install_workalendar(self):
        """安装workalendar"""
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", "workalendar"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("成功", "workalendar安装成功！\n\n请重启程序")
            else:
                messagebox.showerror("失败", f"安装失败:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("错误", f"安装过程中出错: {str(e)}")
