# core/models.py
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class DayType(Enum):
    """日期类型枚举"""
    WORKDAY = ("工作日", 0)
    WEEKEND = ("休息日", 1)
    HOLIDAY = ("节假日", 2)
    MAKEUP = ("调休日", 1)

    def __init__(self, label: str, details_type: int):
        self.label = label
        self.details_type = details_type

    @classmethod
    def from_string(cls, value: str) -> "DayType":
        """从字符串获取枚举值"""
        mapping = {
            "工作日": cls.WORKDAY,
            "休息日": cls.WEEKEND,
            "节假日": cls.HOLIDAY,
            "调休日": cls.MAKEUP,
        }
        return mapping.get(value, cls.WORKDAY)

    @classmethod
    def from_details_type(cls, details_type: int) -> "DayType":
        """从detailsType获取枚举值"""
        if details_type == 0:
            return cls.WORKDAY
        elif details_type == 3:
            return cls.HOLIDAY
        else:
            return cls.WEEKEND


@dataclass
class OvertimeRecord:
    """加班记录数据模型"""
    date: str
    user: str
    day_type: str
    work_hours: float = 0.0
    leave_type: str = "无"
    leave_hours: float = 0.0
    submit_time: str = ""
    salary: str = "0"
    is_leave: bool = False

    def __post_init__(self):
        if not self.submit_time:
            self.submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(self.work_hours, str):
            try:
                self.work_hours = float(self.work_hours)
            except (ValueError, TypeError):
                self.work_hours = 0.0
        if isinstance(self.leave_hours, str):
            try:
                self.leave_hours = float(self.leave_hours)
            except (ValueError, TypeError):
                self.leave_hours = 0.0

    def to_list(self) -> List[str]:
        """转换为CSV列表"""
        return [
            self.date,
            self.user,
            self.day_type,
            str(self.work_hours),
            self.leave_type,
            str(self.leave_hours),
            self.submit_time,
            self.salary
        ]

    @classmethod
    def from_list(cls, data: List[str]) -> "OvertimeRecord":
        """从CSV列表创建"""
        if len(data) < 8:
            data.extend([""] * (8 - len(data)))
        return cls(
            date=data[0],
            user=data[1],
            day_type=data[2],
            work_hours=data[3] if len(data) > 3 else "0",
            leave_type=data[4] if len(data) > 4 else "无",
            leave_hours=data[5] if len(data) > 5 else "0",
            submit_time=data[6] if len(data) > 6 else "",
            salary=data[7] if len(data) > 7 else "0"
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class MonthlySummary:
    """月度汇总数据模型"""
    month: str
    total_hours: float = 0.0
    details: Dict[str, Dict[str, float]] = field(default_factory=dict)
    empty: bool = True

    def __post_init__(self):
        if not self.details:
            self.details = {
                "工作日": {"hours": 0.0, "count": 0},
                "休息日": {"hours": 0.0, "count": 0},
                "节假日": {"hours": 0.0, "count": 0},
                "调休日": {"hours": 0.0, "count": 0},
                "请假": {"hours": 0.0, "count": 0}
            }

    def add_record(self, day_type: str, hours: float):
        """添加记录"""
        self.empty = False
        if day_type in self.details:
            self.details[day_type]["hours"] += hours
            self.details[day_type]["count"] += 1
        self.total_hours = sum(v["hours"] for v in self.details.values())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "month": self.month,
            "total_hours": self.total_hours,
            "details": self.details,
            "empty": self.empty
        }


@dataclass
class HolidayInfo:
    """节假日信息数据模型"""
    date: str
    month: int = 0
    year: int = 0
    week_day: int = 0
    day_type: str = "工作日"
    details_type: int = 0
    type_des: str = "工作日"
    lunar_calendar: str = ""
    solar_terms: str = ""
    chinese_zodiac: str = ""
    constellation: str = ""
    index_work_day: int = 0

    def __post_init__(self):
        if self.month and self.year:
            try:
                date_obj = datetime.strptime(self.date, "%Y-%m-%d")
                self.week_day = date_obj.weekday() + 1
            except ValueError:
                pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "date": self.date,
            "month": self.month,
            "year": self.year,
            "weekDay": self.week_day,
            "type": self.details_type,
            "typeDes": self.type_des,
            "detailsType": self.details_type,
            "dayType": self.day_type,
            "lunarCalendar": self.lunar_calendar,
            "solarTerms": self.solar_terms,
            "chineseZodiac": self.chinese_zodiac,
            "constellation": self.constellation,
            "indexWorkDayOfMonth": self.index_work_day
        }


@dataclass
class SalaryConfig:
    """工资配置数据模型"""
    enabled: bool = False
    hourly_wage: float = 50.0
    weekday_rate: float = 1.0
    weekend_rate: float = 1.5
    holiday_rate: float = 2.0
    deduct_types: List[str] = field(default_factory=lambda: ["事假"])

    def calculate(self, hours: float, day_type: str) -> str:
        """计算加班工资"""
        if not self.enabled or hours <= 0:
            return "0"

        rate = self._get_rate(day_type)
        salary = self.hourly_wage * hours * rate
        return f"{salary:.2f}元"

    def _get_rate(self, day_type: str) -> float:
        """获取倍率"""
        rates = {
            "工作日": self.weekday_rate,
            "休息日": self.weekend_rate,
            "节假日": self.holiday_rate,
            "调休日": 1.5,
        }
        return rates.get(day_type, 1.0)

    def should_deduct(self, leave_type: str) -> bool:
        """判断是否扣除工时"""
        return leave_type in self.deduct_types

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalaryConfig":
        """从字典创建"""
        return cls(
            enabled=data.get("enabled", False),
            hourly_wage=data.get("hourly_wage", 50.0),
            weekday_rate=data.get("weekday_rate", 1.0),
            weekend_rate=data.get("weekend_rate", 1.5),
            holiday_rate=data.get("holiday_rate", 2.0),
            deduct_types=data.get("deduct_types", ["事假"])
        )


@dataclass
class WebhookConfig:
    """Webhook配置数据模型"""
    enabled: bool = False
    url: str = ""
    platform: str = "feishu"
    headers: str = "{}"
    timeout: int = 10
    retry: int = 3
    sync_mode: str = "sync"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookConfig":
        """从字典创建"""
        return cls(
            enabled=data.get("enabled", False),
            url=data.get("url", ""),
            platform=data.get("platform", "feishu"),
            headers=data.get("headers", "{}"),
            timeout=data.get("timeout", 10),
            retry=data.get("retry", 3),
            sync_mode=data.get("sync_mode", "sync")
        )


@dataclass
class SubmitData:
    """提交数据模型"""
    date: str
    user: str
    day_type: str
    is_leave: bool = False
    leave_type: str = ""
    leave_hours: float = 0.0
    work_hours: float = 0.0
    salary: str = "0"
    calculate_salary: bool = False
    submit_method: str = "程序"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubmitData":
        """从字典创建"""
        return cls(
            date=data.get("date", ""),
            user=data.get("user", ""),
            day_type=data.get("day_type", "工作日"),
            is_leave=data.get("is_leave", False),
            leave_type=data.get("leave_type", ""),
            leave_hours=float(data.get("leave_hours", 0)),
            work_hours=float(data.get("work_hours", 0)),
            salary=data.get("salary", "0"),
            calculate_salary=data.get("calculate_salary", False),
            submit_method=data.get("submit_method", "程序")
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
