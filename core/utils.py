# core/utils.py
import socket
from datetime import datetime

def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def validate_date(date_str: str) -> bool:
    """验证日期格式"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_salary(hours: float, day_type: str, overtime_pay: dict) -> str:
    """计算加班工资"""
    if hours <= 0:
        return "0"

    rate = 0
    if day_type == "工作日":
        rate = overtime_pay.get('weekday_rate', 1.5)
    elif day_type == "休息日":
        rate = overtime_pay.get('weekend_rate', 2.0)
    elif day_type == "节假日":
        rate = overtime_pay.get('holiday_rate', 3.0)
    elif day_type == "调休日":
        rate = 1.5

    salary = hours * rate
    return f"{salary:.2f}元"
