# tests/test_utils.py
import pytest
from datetime import datetime
from core.utils import (
    validate_date,
    format_timestamp,
    parse_hours,
    validate_user_name,
    safe_filename,
    truncate_string,
)


class TestValidateDate:
    """测试日期验证"""

    def test_valid_date(self):
        """测试有效日期"""
        assert validate_date("2024-01-15") is True
        assert validate_date("2024-12-31") is True
        assert validate_date("2024-02-29") is True

    def test_invalid_date(self):
        """测试无效日期"""
        assert validate_date("2024-13-01") is False
        assert validate_date("2024-02-30") is False
        assert validate_date("invalid") is False
        assert validate_date("") is False
        assert validate_date(None) is False

    def test_leap_year(self):
        """测试闰年"""
        assert validate_date("2024-02-29") is True
        assert validate_date("2023-02-29") is False


class TestParseHours:
    """测试小时数解析"""

    def test_valid_hours(self):
        """测试有效小时数"""
        success, hours = parse_hours("8")
        assert success is True
        assert hours == 8.0

        success, hours = parse_hours("8.5")
        assert success is True
        assert hours == 8.5

    def test_invalid_hours(self):
        """测试无效小时数"""
        success, hours = parse_hours("invalid")
        assert success is False
        assert hours == 0.0

        success, hours = parse_hours("")
        assert success is False

    def test_negative_hours(self):
        """测试负数小时数"""
        success, hours = parse_hours("-4")
        assert success is True
        assert hours == -4.0


class TestValidateUserName:
    """测试用户名验证"""

    def test_valid_name(self):
        """测试有效用户名"""
        success, msg = validate_user_name("张三")
        assert success is True
        assert msg == ""

        success, msg = validate_user_name("zhang_san")
        assert success is True

        success, msg = validate_user_name("ZhangSan123")
        assert success is True

    def test_invalid_name(self):
        """测试无效用户名"""
        success, msg = validate_user_name("")
        assert success is False
        assert "不能为空" in msg

        success, msg = validate_user_name("   ")
        assert success is False

        success, msg = validate_user_name("x" * 51)
        assert success is False
        assert "过长" in msg

        success, msg = validate_user_name("zhang-san")
        assert success is False


class TestSafeFilename:
    """测试安全文件名"""

    def test_safe_name(self):
        """测试安全文件名"""
        assert safe_filename("normal_file.txt") == "normal_file.txt"
        assert safe_filename("加班记录_2024.xlsx") == "加班记录_2024.xlsx"

    def test_unsafe_name(self):
        """测试不安全文件名"""
        assert safe_filename("file<>:txt") == "file___txt"
        assert safe_filename("file|test.txt") == "file_test.txt"


class TestTruncateString:
    """测试字符串截断"""

    def test_short_string(self):
        """测试短字符串"""
        result = truncate_string("short", 10)
        assert result == "short"

    def test_long_string(self):
        """测试长字符串"""
        long_str = "x" * 150
        result = truncate_string(long_str, 100)
        assert len(result) == 100
        assert result.endswith("...")


class TestFormatTimestamp:
    """测试时间戳格式化"""

    def test_format(self):
        """测试格式"""
        result = format_timestamp()
        assert isinstance(result, str)
        assert len(result) == 19
        assert result[4] == "-"
        assert result[10] == " "


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
