# core/utils.py
import socket
import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any


def validate_date(date_string: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    if not date_string:
        return False
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def format_timestamp() -> str:
    """格式化当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def get_web_service_url(port: int = 8080) -> str:
    """获取Web服务完整URL"""
    ip = get_local_ip()
    if ip == "localhost":
        return f"http://localhost:{port}"
    return f"http://{ip}:{port}"


def calculate_salary(
    hours: float,
    day_type: str,
    overtime_pay: Dict[str, Any]
) -> str:
    """计算加班工资"""
    if hours <= 0:
        return "0"

    rate = _get_rate_by_day_type(day_type, overtime_pay)
    salary = hours * rate
    return f"{salary:.2f}元"


def _get_rate_by_day_type(
    day_type: str,
    overtime_pay: Dict[str, Any]
) -> float:
    """根据日期类型获取倍率"""
    rate_mapping = {
        "工作日": overtime_pay.get('weekday_rate', 1.5),
        "休息日": overtime_pay.get('weekend_rate', 2.0),
        "节假日": overtime_pay.get('holiday_rate', 3.0),
        "调休日": 1.5,
    }
    return rate_mapping.get(day_type, 1.0)


def parse_hours(hours_str: str) -> Tuple[bool, float]:
    """安全解析小时数

    Returns:
        Tuple[成功标志, 解析结果或0]
    """
    try:
        hours = float(hours_str)
        return True, hours
    except (ValueError, TypeError):
        return False, 0.0


def validate_user_name(user: str) -> Tuple[bool, str]:
    """验证用户名

    Returns:
        Tuple[是否有效, 错误信息]
    """
    if not user or not user.strip():
        return False, "用户名不能为空"
    if len(user) > 50:
        return False, "用户名过长（最多50字符）"
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', user):
        return False, "用户名只能包含中文、字母、数字和下划线"
    return True, ""


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def truncate_string(s: str, max_length: int = 100) -> str:
    """截断字符串到指定长度"""
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."
