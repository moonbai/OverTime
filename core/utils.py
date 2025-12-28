# core/utils.py
import socket
import re
from datetime import datetime

def validate_date(date_string):
    """验证日期格式 YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_timestamp():
    """格式化当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个UDP socket连接到外部地址（不实际发送）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # 如果失败，返回localhost
        return "localhost"

def get_web_service_url(port=8080):
    """获取Web服务完整URL"""
    ip = get_local_ip()
    if ip == "localhost":
        return f"http://localhost:{port}"
    return f"http://{ip}:{port}"

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
