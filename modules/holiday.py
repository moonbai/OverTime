# modules/holiday.py
import json
import os
from datetime import datetime

class HolidayChecker:
    """节假日检查器 - 支持API格式JSON"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.calendar_available = False
        self.holiday_data = {}

        # 检测 chinese_calendar
        try:
            import chinese_calendar
            self.calendar_available = True
            print("✓ chinese_calendar 已安装")
        except ImportError:
            print("⚠ chinese_calendar 未安装")

        # 加载节假日JSON配置
        config_file = os.path.join("modules", "holiday.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 🎯 检查是否是API响应格式（有code, msg, data字段）
                if isinstance(data, dict) and "data" in data and "code" in data:
                    print(f"检测到API响应格式，提取data字段")
                    data = data["data"]

                # 检测格式并转换
                if isinstance(data, list) and len(data) > 0 and "days" in data[0]:
                    # API格式：[{month: 1, year: 2026, days: [...]}]
                    self.holiday_data = self._convert_api_format(data)
                    print(f"✓ holiday.json API格式加载成功")
                elif isinstance(data, dict) and any("month" in v for v in data.values() if isinstance(v, list)):
                    # API格式：{"2026": [{month: 1, days: [...]}]}
                    self.holiday_data = {}
                    for year, months in data.items():
                        self.holiday_data[year] = self._convert_api_format(months)
                    print(f"✓ holiday.json API格式（按年）加载成功")
                else:
                    # 原始格式：{"2024": {"01-01": {...}}}
                    self.holiday_data = data
                    print(f"✓ holiday.json 原始格式加载成功")

                # 打印支持的年份
                if self.holiday_data:
                    years = list(self.holiday_data.keys())
                    print(f"支持年份: {years}")

                    # 验证第一个年份的数据
                    if years:
                        first_year = years[0]
                        if first_year in self.holiday_data:
                            dates = list(self.holiday_data[first_year].keys())[:3]
                            print(f"  {first_year} 示例日期: {dates}")
                            # 打印第一个日期的详细信息
                            if dates:
                                first_date = dates[0]
                                config = self.holiday_data[first_year][first_date]
                                print(f"  {first_year}-{first_date}: type={config['type']}, detailsType={config['detailsType']}, typeDes={config['typeDes']}")

            except Exception as e:
                print(f"⚠ holiday.json 加载失败: {e}")
                self.holiday_data = {}
        else:
            print(f"⚠ holiday.json 不存在: {config_file}")
            self.holiday_data = {}

    def _convert_api_format(self, api_data):
        """转换API格式为内部格式"""
        result = {}
        for month_data in api_data:
            month = month_data.get("month")
            year = month_data.get("year")
            if not month or not year:
                continue

            year_str = str(year)
            if year_str not in result:
                result[year_str] = {}

            for day_data in month_data.get("days", []):
                date_str = day_data["date"]
                month_day = date_str[5:10]

                result[year_str][month_day] = {
                    "type": day_data["type"],
                    "typeDes": day_data["typeDes"],
                    "detailsType": day_data["detailsType"],
                    "chineseZodiac": day_data.get("chineseZodiac", ""),
                    "solarTerms": day_data.get("solarTerms", ""),
                    "lunarCalendar": day_data.get("lunarCalendar", ""),
                    "avoid": day_data.get("avoid", ""),
                    "suit": day_data.get("suit", ""),
                    "weekDay": day_data.get("weekDay", 0),
                    "yearTips": day_data.get("yearTips", ""),
                    "dayOfYear": day_data.get("dayOfYear", 0),
                    "weekOfYear": day_data.get("weekOfYear", 0),
                    "constellation": day_data.get("constellation", ""),
                    "indexWorkDayOfMonth": day_data.get("indexWorkDayOfMonth", 0)
                }

        return result

    def get_holiday_info(self, date_str: str) -> dict:
        """获取节假日详细信息"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
            month_day = f"{month:02d}-{day:02d}"

            # 基础信息
            result = {
                "month": month,
                "year": year,
                "date": date_str,
                "weekDay": date_obj.weekday() + 1,
                "yearTips": "",
                "chineseZodiac": "",
                "solarTerms": "",
                "lunarCalendar": "",
                "suit": "",
                "avoid": "",
                "dayOfYear": date_obj.timetuple().tm_yday,
                "weekOfYear": date_obj.isocalendar()[1],
                "constellation": self._get_constellation(month, day),
                "type": 0,
                "typeDes": "工作日",
                "detailsType": 0,
                "indexWorkDayOfMonth": 0
            }

            # 检查配置
            use_builtin = self.config_manager.get('use_builtin_holiday', False)

            if use_builtin and self.holiday_data:
                year_str = str(year)

                if year_str in self.holiday_data and month_day in self.holiday_data[year_str]:
                    config = self.holiday_data[year_str][month_day]

                    # 填充所有字段
                    result["type"] = config["type"]
                    result["typeDes"] = config["typeDes"]
                    result["detailsType"] = config["detailsType"]
                    result["chineseZodiac"] = config.get("chineseZodiac", "")
                    result["solarTerms"] = config.get("solarTerms", "")
                    result["lunarCalendar"] = config.get("lunarCalendar", "")
                    result["avoid"] = config.get("avoid", "")
                    result["suit"] = config.get("suit", "")
                    result["yearTips"] = config.get("yearTips", "")
                    result["dayOfYear"] = config.get("dayOfYear", result["dayOfYear"])
                    result["weekOfYear"] = config.get("weekOfYear", result["weekOfYear"])
                    result["constellation"] = config.get("constellation", result["constellation"])
                    result["indexWorkDayOfMonth"] = config.get("indexWorkDayOfMonth", 0)

                    if config["type"] == 0 and result["indexWorkDayOfMonth"] == 0:
                        result["indexWorkDayOfMonth"] = self._get_workday_index(date_obj)

                    return result
                else:
                    # 未命中 - 默认判断
                    is_weekend = date_obj.weekday() >= 5
                    if is_weekend:
                        result["type"] = 1
                        result["typeDes"] = "休息日"
                        result["detailsType"] = 1
                    else:
                        result["type"] = 0
                        result["typeDes"] = "工作日"
                        result["detailsType"] = 0
                        result["indexWorkDayOfMonth"] = self._get_workday_index(date_obj)
                    return result

            # 未选择内置数据 - 使用chinese_calendar
            if self.calendar_available:
                try:
                    import chinese_calendar as calendar

                    is_holiday, holiday_name = calendar.get_holiday_detail(date_obj.date())
                    is_in_lieu = calendar.is_in_lieu(date_obj.date())
                    is_workday = calendar.is_workday(date_obj.date())

                    if is_in_lieu:
                        result["type"] = 1
                        result["typeDes"] = holiday_name.value if holiday_name else "调休"
                        result["detailsType"] = 1
                        return result

                    if is_holiday:
                        result["type"] = 2
                        result["typeDes"] = holiday_name.value if holiday_name else "节假日"
                        if "国庆" in str(holiday_name) or "春节" in str(holiday_name):
                            result["detailsType"] = 3
                        else:
                            result["detailsType"] = 2
                        return result

                    if is_workday:
                        result["type"] = 0
                        result["typeDes"] = "工作日"
                        result["detailsType"] = 0
                        result["indexWorkDayOfMonth"] = self._get_workday_index(date_obj)
                        return result

                except Exception as e:
                    print(f"chinese_calendar调用失败: {e}")

            # 默认：检查周末
            is_weekend = date_obj.weekday() >= 5
            if is_weekend:
                result["type"] = 1
                result["typeDes"] = "休息日"
                result["detailsType"] = 1
            else:
                result["type"] = 0
                result["typeDes"] = "工作日"
                result["detailsType"] = 0
                result["indexWorkDayOfMonth"] = self._get_workday_index(date_obj)

            return result

        except Exception as e:
            print(f"⚠ 获取节假日信息失败: {e}")
            return {
                "month": 0, "year": 0, "date": date_str, "weekDay": 0,
                "yearTips": "", "type": 0, "typeDes": "未知", "detailsType": 0,
                "chineseZodiac": "", "solarTerms": "", "lunarCalendar": "",
                "avoid": "", "suit": "", "dayOfYear": 0, "weekOfYear": 0,
                "constellation": "", "indexWorkDayOfMonth": 0
            }

    def get_day_type(self, date_str: str) -> tuple:
        """获取日期类型：(类型, 原因) - 按detailsType分类"""
        info = self.get_holiday_info(date_str)

        # 按detailsType分类：
        # detailsType=0: 工作日
        # detailsType=1: 休息日
        # detailsType=2: 普通节假日 → 休息日
        # detailsType=3: 三倍工资节假日 → 节假日

        if info["detailsType"] == 0:
            return ("工作日", info["typeDes"])
        elif info["detailsType"] == 1:
            return ("休息日", info["typeDes"])
        elif info["detailsType"] == 2:
            return ("休息日", f"{info['typeDes']}(普通节假日)")
        elif info["detailsType"] == 3:
            return ("节假日", f"{info['typeDes']}(三倍)")
        else:
            return ("未知", "未知")

    def _get_constellation(self, month: int, day: int) -> str:
        """获取星座"""
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "白羊座"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "金牛座"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
            return "双子座"
        elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
            return "巨蟹座"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "狮子座"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "处女座"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 23):
            return "天秤座"
        elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
            return "天蝎座"
        elif (month == 11 and day >= 23) or (month == 12 and day <= 21):
            return "射手座"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "摩羯座"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "水瓶座"
        else:
            return "双鱼座"

    def _get_workday_index(self, date_obj: datetime) -> int:
        """获取当月第几个工作日"""
        year = date_obj.year
        month = date_obj.month
        workday_count = 0

        for day in range(1, 32):
            try:
                current_date = datetime(year, month, day)
                if current_date.month != month:
                    break

                is_weekend = current_date.weekday() >= 5
                if is_weekend:
                    continue

                month_day = f"{month:02d}-{day:02d}"
                year_str = str(year)

                if year_str in self.holiday_data and month_day in self.holiday_data[year_str]:
                    config = self.holiday_data[year_str][month_day]
                    if config["type"] != 0:
                        continue

                workday_count += 1
                if current_date == date_obj:
                    return workday_count
            except:
                continue

        return 0

    def get_supported_years(self) -> list:
        """获取支持的年份 - 根据数据源返回"""
        use_builtin = self.config_manager.get('use_builtin_holiday', False)

        if use_builtin:
            # 内置数据：返回holiday.json中的年份
            years = list(self.holiday_data.keys())
            if years:
                return sorted(years)
            else:
                # 如果没有数据，返回默认值
                return ["2024", "2025", "2026"]
        else:
            # chinese_calendar：返回2004-2026
            if self.calendar_available:
                return ["2004", "2005", "2006", "2007", "2008", "2009", "2010",
                        "2011", "2012", "2013", "2014", "2015", "2016", "2017",
                        "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
            else:
                # 两者都没有，返回默认值
                return ["2024", "2025", "2026"]
