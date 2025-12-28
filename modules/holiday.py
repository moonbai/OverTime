# modules/holiday.py
from datetime import datetime

class HolidayChecker:
    """节假日检查器"""
    def __init__(self, use_workalendar=True):
        self.workalendar_available = False
        self.holidays = {}

        # 尝试导入workalendar
        if use_workalendar:
            try:
                from workalendar.china import China
                self.workalendar_available = True
                self.china_calendar = China()
                print("✓ workalendar 已集成")
            except ImportError:
                self.workalendar_available = False
                print("⚠ workalendar 未安装，使用内置数据")

        # 内置节假日数据（2024、2025、2026年）
        self.holidays = {
            "2024": {
                # 节假日
                "01-01": ("节假日", "元旦"),
                "02-10": ("节假日", "春节"),
                "02-11": ("节假日", "春节"),
                "02-12": ("节假日", "春节"),
                "04-04": ("节假日", "清明节"),
                "05-01": ("节假日", "劳动节"),
                "06-10": ("节假日", "端午节"),
                "09-17": ("节假日", "中秋节"),
                "10-01": ("节假日", "国庆节"),
                "10-02": ("节假日", "国庆节"),
                "10-03": ("节假日", "国庆节"),
                # 调休日
                "01-04": ("调休日", "元旦调休"),
                "02-04": ("调休日", "春节调休"),
                "02-18": ("调休日", "春节调休"),
                "04-07": ("调休日", "清明调休"),
                "05-02": ("调休日", "劳动节调休"),
                "06-11": ("调休日", "端午调休"),
                "09-18": ("调休日", "中秋调休"),
                "10-07": ("调休日", "国庆调休"),
            },
            "2025": {
                # 节假日
                "01-01": ("节假日", "元旦"),
                "01-28": ("节假日", "春节"),
                "01-29": ("节假日", "春节"),
                "01-30": ("节假日", "春节"),
                "01-31": ("节假日", "春节"),
                "02-01": ("节假日", "春节"),
                "02-02": ("节假日", "春节"),
                "04-04": ("节假日", "清明节"),
                "05-01": ("节假日", "劳动节"),
                "05-02": ("节假日", "劳动节"),
                "05-03": ("节假日", "劳动节"),
                "06-01": ("节假日", "儿童节"),
                "06-19": ("节假日", "端午节"),
                "10-01": ("节假日", "国庆节"),
                "10-02": ("节假日", "国庆节"),
                "10-03": ("节假日", "国庆节"),
                "10-04": ("节假日", "国庆节"),
                "10-05": ("节假日", "国庆节"),
                "10-06": ("节假日", "国庆节"),
                "10-07": ("节假日", "国庆节"),
                "10-08": ("节假日", "国庆节"),
                "10-29": ("节假日", "重阳节"),
                # 调休日
                "01-26": ("调休日", "春节调休"),
                "02-08": ("调休日", "春节调休"),
                "04-07": ("调休日", "清明调休"),
                "05-06": ("调休日", "劳动节调休"),
                "06-02": ("调休日", "儿童节调休"),
                "06-20": ("调休日", "端午调休"),
                "10-09": ("调休日", "国庆调休"),
                "10-10": ("调休日", "国庆调休"),
            },
            "2026": {
                # 节假日
                "01-01": ("节假日", "元旦"),
                "02-17": ("节假日", "春节"),
                "02-18": ("节假日", "春节"),
                "02-19": ("节假日", "春节"),
                "04-05": ("节假日", "清明节"),
                "05-01": ("节假日", "劳动节"),
                "06-19": ("节假日", "端午节"),
                "10-01": ("节假日", "国庆节"),
                "10-02": ("节假日", "国庆节"),
                "10-03": ("节假日", "国庆节"),
                # 调休日
                "01-04": ("调休日", "元旦调休"),
                "02-15": ("调休日", "春节调休"),
                "02-22": ("调休日", "春节调休"),
                "05-02": ("调休日", "劳动节调休"),
                "10-08": ("调休日", "国庆调休"),
                "10-09": ("调休日", "国庆调休"),
            }
        }

    def get_day_type(self, date_str: str) -> tuple:
        """获取日期类型：(类型, 原因)"""
        try:
            # 1. 优先使用workalendar
            if self.workalendar_available and hasattr(self, 'china_calendar'):
                try:
                    year = int(date_str.split('-')[0])

                    # 检查是否是节假日
                    if self.china_calendar.is_holiday(date_str):
                        # 获取节日名称
                        holidays = self.china_calendar.holidays(year)
                        for h_date, h_name in holidays:
                            if str(h_date) == date_str:
                                return ("节假日", h_name)
                        return ("节假日", "节假日")

                    # 检查是否是工作日
                    if self.china_calendar.is_working_day(date_str):
                        # 检查是否是调休日（周六日上班）
                        month_day = date_str[5:]
                        if year == 2024 and month_day in self.holidays["2024"]:
                            h_type, h_name = self.holidays["2024"][month_day]
                            if h_type == "调休日":
                                return ("调休日", h_name)
                        return ("工作日", "工作日")
                    else:
                        return ("休息日", "周末")

                except Exception as e:
                    print(f"workalendar调用失败: {e},切换到手动模式")

            # 2. 使用内置数据
            year = date_str.split('-')[0]
            month_day = date_str[5:]  # MM-DD

            if year in self.holidays and month_day in self.holidays[year]:
                return self.holidays[year][month_day]

            # 3. 基础判断
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date_obj.weekday()

            if weekday < 5:
                return ("工作日", "工作日")
            else:
                return ("休息日", "周末")

        except Exception as e:
            print(f"⚠判断日期类型失败: {e}")
            return ("未知", "判断失败")

    def get_supported_years(self) -> list:
        """获取支持的年份"""
        if self.workalendar_available:
            return ["2024", "2025", "2026", "2027", "2028", "2029", "2030"]
        else:
            return ["2024", "2025", "2026"]  # 内置数据支持2024-2026
