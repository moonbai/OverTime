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

        # 内置节假日数据
        self.holidays = {
            "2024": {
                "01-01": ("节假日", "元旦"), "02-10": ("节假日", "春节"), "02-11": ("节假日", "春节"),
                "02-12": ("节假日", "春节"), "04-04": ("节假日", "清明节"), "05-01": ("节假日", "劳动节"),
                "06-10": ("节假日", "端午节"), "09-17": ("节假日", "中秋节"), "10-01": ("节假日", "国庆节"),
                "10-02": ("节假日", "国庆节"), "10-03": ("节假日", "国庆节"),
                "01-04": ("调休日", "元旦调休"), "02-04": ("调休日", "春节调休"), "02-18": ("调休日", "春节调休"),
                "04-07": ("调休日", "清明调休"), "05-02": ("调休日", "劳动节调休"), "06-11": ("调休日", "端午调休"),
                "09-18": ("调休日", "中秋调休"), "10-07": ("调休日", "国庆调休"),
            },
            "2026": {
                "01-01": ("节假日", "元旦"), "02-17": ("节假日", "春节"), "02-18": ("节假日", "春节"),
                "02-19": ("节假日", "春节"), "04-05": ("节假日", "清明节"), "05-01": ("节假日", "劳动节"),
                "06-19": ("节假日", "端午节"), "10-01": ("节假日", "国庆节"), "10-02": ("节假日", "国庆节"),
                "10-03": ("节假日", "国庆节"),
                "01-04": ("调休日", "元旦调休"), "02-15": ("调休日", "春节调休"), "02-22": ("调休日", "春节调休"),
                "05-02": ("调休日", "劳动节调休"), "10-08": ("调休日", "国庆调休"), "10-09": ("调休日", "国庆调休"),
            }
        }

    def get_day_type(self, date_str: str) -> tuple:
        """获取日期类型：(类型, 原因)"""
        try:
            if self.workalendar_available and hasattr(self, 'china_calendar'):
                try:
                    year = int(date_str.split('-')[0])
                    if self.china_calendar.is_holiday(date_str):
                        holidays = self.china_calendar.holidays(year)
                        for h_date, h_name in holidays:
                            if str(h_date) == date_str:
                                return ("节假日", h_name)
                        return ("节假日", "节假日")
                    if self.china_calendar.is_working_day(date_str):
                        month_day = date_str[5:]
                        if year == 2024 and month_day in self.holidays["2024"]:
                            h_type, h_name = self.holidays["2024"][month_day]
                            if h_type == "调休日":
                                return ("调休日", h_name)
                        return ("工作日", "工作日")
                    return ("休息日", "周末")
                except Exception:
                    pass

            year = date_str.split('-')[0]
            month_day = date_str[5:]
            if year in self.holidays and month_day in self.holidays[year]:
                return self.holidays[year][month_day]

            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date_obj.weekday()
            if weekday < 5:
                return ("工作日", "工作日")
            return ("休息日", "周末")
        except:
            return ("未知", "判断失败")

    def get_supported_years(self) -> list:
        if self.workalendar_available:
            return ["2024", "2025", "2026", "2027", "2028", "2029", "2030"]
        return list(self.holidays.keys())
