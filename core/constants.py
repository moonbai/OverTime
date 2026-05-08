# core/constants.py
from enum import Enum
from typing import Final


APP_NAME: Final[str] = "加班管理系统"
APP_VERSION: Final[str] = "2.0.0"
DEFAULT_PORT: Final[int] = 8080
DEFAULT_PAGE_SIZE: Final[int] = 10
DEFAULT_HOURS: Final[str] = "8"

DEFAULT_LEAVE_TYPES: list = [
    "事假",
    "病假",
    "年假",
    "婚假",
    "产假",
]

DEFAULT_DEDUCT_TYPES: list = ["事假"]

DEFAULT_SALARY_CONFIG: dict = {
    "enabled": False,
    "hourly_wage": 50.0,
    "weekday_rate": 1.0,
    "weekend_rate": 1.5,
    "holiday_rate": 2.0,
    "deduct_types": ["事假"]
}

SUPPORTED_WEBHOOK_PLATFORMS: dict = {
    "feishu": {
        "name": "飞书",
        "url_hint": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx",
        "format": "interactive"
    },
    "dingtalk": {
        "name": "钉钉",
        "url_hint": "https://oapi.dingtalk.com/robot/send?access_token=xxxx",
        "format": "markdown"
    },
    "wechat": {
        "name": "企业微信",
        "url_hint": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx",
        "format": "text"
    },
    "lark": {
        "name": "Lark",
        "url_hint": "https://open.larksuite.com/open-apis/bot/v2/hook/xxxx",
        "format": "interactive"
    },
    "slack": {
        "name": "Slack",
        "url_hint": "https://hooks.slack.com/services/XXXX/XXXX/XXXX",
        "format": "json"
    },
    "custom": {
        "name": "自定义",
        "url_hint": "任意Webhook URL",
        "format": "json"
    }
}


class DayTypeEnum(str, Enum):
    """日期类型枚举"""
    WORKDAY = "工作日"
    WEEKEND = "休息日"
    HOLIDAY = "节假日"
    MAKEUP = "调休日"

    @classmethod
    def values(cls) -> list:
        return [e.value for e in cls]


class LeaveTypeEnum(str, Enum):
    """请假类型枚举"""
    PERSONAL = "事假"
    SICK = "病假"
    ANNUAL = "年假"
    MARRIAGE = "婚假"
    MATERNITY = "产假"

    @classmethod
    def values(cls) -> list:
        return [e.value for e in cls]


class WebhookPlatformEnum(str, Enum):
    """Webhook平台枚举"""
    FEISHU = "feishu"
    DINGTALK = "dingtalk"
    WECHAT = "wechat"
    LARK = "lark"
    SLACK = "slack"
    CUSTOM = "custom"


class RecordStatus(str, Enum):
    """记录状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ConfigKeys:
    """配置键名常量"""
    LAST_USER = "last_user"
    DEFAULT_HOURS = "default_hours"
    PAGE_SIZE = "page_size"
    WEB_PORT = "web_port"
    LEAVE_TYPES = "leave_types"
    DEDUCT_REST_DAY_HOURS = "deduct_rest_day_hours"
    OVERTIME_PAY = "overtime_pay"
    WEBHOOK = "webhook"
    MODULES = "modules"
    USE_BUILTIN_HOLIDAY = "use_builtin_holiday"


DATA_FILE_HEADERS: list = [
    "日期",
    "用户",
    "类型",
    "加班时长",
    "请假类型",
    "请假时长",
    "提交时间",
    "加班工资"
]

DATA_DIR: str = "data"
BACKUP_DIR: str = "backup"
CONFIG_FILE: str = "config.json"
DATA_FILE: str = "overtime_records.csv"
HOLIDAY_FILE: str = "modules/holiday.json"
ERROR_LOG_FILE: str = "error_log.txt"

CSV_ENCODINGS: list = ["utf-8-sig", "utf-8", "gbk", "gb2312"]
