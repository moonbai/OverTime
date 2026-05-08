# tests/test_models.py
import pytest
from datetime import datetime
from core.models import (
    OvertimeRecord,
    MonthlySummary,
    HolidayInfo,
    SalaryConfig,
    SubmitData,
    DayType,
)


class TestOvertimeRecord:
    """测试加班记录数据模型"""

    def test_create_record(self):
        """测试创建记录"""
        record = OvertimeRecord(
            date="2024-01-15",
            user="张三",
            day_type="工作日",
            work_hours=8.0
        )
        assert record.date == "2024-01-15"
        assert record.user == "张三"
        assert record.day_type == "工作日"
        assert record.work_hours == 8.0

    def test_to_list(self):
        """测试转换为列表"""
        record = OvertimeRecord(
            date="2024-01-15",
            user="张三",
            day_type="工作日",
            work_hours=8.0,
            salary="400.00元"
        )
        result = record.to_list()
        assert len(result) == 8
        assert result[0] == "2024-01-15"
        assert result[1] == "张三"

    def test_from_list(self):
        """测试从列表创建"""
        data = ["2024-01-15", "张三", "工作日", "8.0", "无", "0", "2024-01-15 10:00:00", "400.00元"]
        record = OvertimeRecord.from_list(data)
        assert record.date == "2024-01-15"
        assert record.user == "张三"
        assert record.work_hours == 8.0

    def test_string_hours_conversion(self):
        """测试字符串小时数转换"""
        record = OvertimeRecord(
            date="2024-01-15",
            user="张三",
            day_type="工作日",
            work_hours="8.0"
        )
        assert isinstance(record.work_hours, float)
        assert record.work_hours == 8.0


class TestMonthlySummary:
    """测试月度汇总数据模型"""

    def test_create_summary(self):
        """测试创建汇总"""
        summary = MonthlySummary(month="2024-01")
        assert summary.month == "2024-01"
        assert summary.empty is True
        assert summary.total_hours == 0

    def test_add_record(self):
        """测试添加记录"""
        summary = MonthlySummary(month="2024-01")
        summary.add_record("工作日", 8.0)
        summary.add_record("工作日", 4.0)

        assert summary.empty is False
        assert summary.details["工作日"]["hours"] == 12.0
        assert summary.details["工作日"]["count"] == 2
        assert summary.total_hours == 12.0

    def test_to_dict(self):
        """测试转换为字典"""
        summary = MonthlySummary(month="2024-01")
        summary.add_record("休息日", 8.0)
        result = summary.to_dict()

        assert result["month"] == "2024-01"
        assert result["empty"] is False
        assert "details" in result


class TestSalaryConfig:
    """测试工资配置数据模型"""

    def test_create_config(self):
        """测试创建配置"""
        config = SalaryConfig(
            enabled=True,
            hourly_wage=50.0,
            weekday_rate=1.5
        )
        assert config.enabled is True
        assert config.hourly_wage == 50.0

    def test_calculate_salary(self):
        """测试工资计算"""
        config = SalaryConfig(
            enabled=True,
            hourly_wage=50.0,
            weekday_rate=1.5
        )

        result = config.calculate(8.0, "工作日")
        assert result == "600.00元"

        result = config.calculate(0, "工作日")
        assert result == "0"

    def test_calculate_disabled(self):
        """测试禁用状态"""
        config = SalaryConfig(enabled=False)
        result = config.calculate(8.0, "工作日")
        assert result == "0"

    def test_should_deduct(self):
        """测试扣除判断"""
        config = SalaryConfig(deduct_types=["事假", "病假"])
        assert config.should_deduct("事假") is True
        assert config.should_deduct("年假") is False

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "enabled": True,
            "hourly_wage": 60.0,
            "weekday_rate": 1.5,
            "weekend_rate": 2.0,
            "holiday_rate": 3.0,
            "deduct_types": ["事假"]
        }
        config = SalaryConfig.from_dict(data)
        assert config.hourly_wage == 60.0
        assert "事假" in config.deduct_types


class TestDayType:
    """测试日期类型枚举"""

    def test_from_string(self):
        """测试从字符串获取"""
        assert DayType.from_string("工作日") == DayType.WORKDAY
        assert DayType.from_string("休息日") == DayType.WEEKEND
        assert DayType.from_string("节假日") == DayType.HOLIDAY
        assert DayType.from_string("调休日") == DayType.MAKEUP

    def test_from_details_type(self):
        """测试从detailsType获取"""
        assert DayType.from_details_type(0) == DayType.WORKDAY
        assert DayType.from_details_type(1) == DayType.WEEKEND
        assert DayType.from_details_type(2) == DayType.WEEKEND
        assert DayType.from_details_type(3) == DayType.HOLIDAY


class TestSubmitData:
    """测试提交数据模型"""

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "date": "2024-01-15",
            "user": "张三",
            "day_type": "工作日",
            "work_hours": "8",
            "is_leave": False
        }
        submit = SubmitData.from_dict(data)
        assert submit.date == "2024-01-15"
        assert submit.user == "张三"
        assert submit.work_hours == 8.0

    def test_to_dict(self):
        """测试转换为字典"""
        submit = SubmitData(
            date="2024-01-15",
            user="张三",
            day_type="工作日"
        )
        result = submit.to_dict()
        assert isinstance(result, dict)
        assert result["date"] == "2024-01-15"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
