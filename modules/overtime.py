# modules/overtime.py
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from core.models import MonthlySummary, OvertimeRecord


class OvertimeModule:
    """加班统计模块"""

    def __init__(
        self,
        data_manager,
        holiday_checker,
        config_manager
    ):
        self.data_manager = data_manager
        self.holiday_checker = holiday_checker
        self.config_manager = config_manager

    def get_monthly_summary(self, month: Optional[str] = None) -> Dict[str, Any]:
        """获取月度汇总统计"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        records = self.data_manager.get_monthly_records(month)
        if not records:
            return MonthlySummary(month=month).to_dict()

        summary = MonthlySummary(month=month)

        for record_data in records:
            if len(record_data) < 4:
                continue

            record = self._parse_record(record_data)
            summary.add_record(record.day_type, record.work_hours)

        return summary.to_dict()

    def _parse_record(self, record_data: list) -> OvertimeRecord:
        """解析记录数据"""
        if len(record_data) < 8:
            record_data.extend([""] * (8 - len(record_data)))

        return OvertimeRecord(
            date=record_data[0],
            user=record_data[1],
            day_type=record_data[2],
            work_hours=record_data[3] if record_data[3] else "0",
            leave_type=record_data[4] if len(record_data) > 4 else "无",
            leave_hours=record_data[5] if len(record_data) > 5 else "0",
            submit_time=record_data[6] if len(record_data) > 6 else "",
            salary=record_data[7] if len(record_data) > 7 else "0"
        )

    def submit_overtime(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[list]]:
        """提交加班记录

        Args:
            data: 包含以下字段的字典:
                - user: 用户名
                - date: 日期
                - day_type: 日期类型
                - work_hours: 加班时长
                - leave_type: 请假类型
                - leave_hours: 请假时长
                - is_leave: 是否请假
                - salary: 工资
                - calculate_salary: 是否计算工资

        Returns:
            Tuple[成功标志, 消息, 记录列表]
        """
        is_valid, error_msg = self._validate_submit_data(data)
        if not is_valid:
            return False, error_msg, None

        self._warn_type_mismatch(data)

        record = self._build_record(data)
        success = self.data_manager.add_record(record)

        if success:
            return True, "记录已保存", record
        return False, "保存失败", None

    def _validate_submit_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证提交数据"""
        required_fields = ['user', 'date', 'day_type']
        for field in required_fields:
            if not data.get(field):
                return False, f"缺少必填字段: {field}"
        return True, ""

    def _warn_type_mismatch(self, data: Dict[str, Any]) -> None:
        """警告类型不匹配"""
        if not self.holiday_checker or data.get('is_leave'):
            return

        detected_type, reason = self.holiday_checker.get_day_type(data['date'])
        if detected_type != data['day_type']:
            print(f"⚠️ 类型不匹配: {data['date']} 检测到 {detected_type}({reason})，用户选择 {data['day_type']}")

    def _build_record(self, data: Dict[str, Any]) -> list:
        """构建记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        salary = data.get('salary', '0') if data.get('calculate_salary', False) else "0"

        if data.get('is_leave'):
            return self._build_leave_record(data, timestamp, salary)
        return self._build_overtime_record(data, timestamp, salary)

    def _build_leave_record(
        self,
        data: Dict[str, Any],
        timestamp: str,
        salary: str
    ) -> list:
        """构建请假记录"""
        leave_type = data.get('leave_type', '')
        is_deduct = leave_type == "事假"

        day_type = "休息日" if is_deduct else data.get('day_type', '工作日')
        work_hours = data.get('leave_hours', '0') if is_deduct else "0"
        leave_hours = data.get('leave_hours', '0') if is_deduct else "无"

        return [
            data['date'],
            data['user'],
            day_type,
            work_hours,
            leave_type,
            leave_hours,
            timestamp,
            salary
        ]

    def _build_overtime_record(
        self,
        data: Dict[str, Any],
        timestamp: str,
        salary: str
    ) -> list:
        """构建加班记录"""
        return [
            data['date'],
            data['user'],
            data['day_type'],
            data.get('work_hours', '0'),
            "无",
            "无",
            timestamp,
            salary
        ]

    def get_year_summary(self, year: Optional[str] = None) -> Dict[str, Any]:
        """获取年度汇总"""
        if year is None:
            year = datetime.now().strftime("%Y")

        monthly_summaries = {}
        for month in range(1, 13):
            month_str = f"{year}-{month:02d}"
            summary = self.get_monthly_summary(month_str)
            if not summary.get('empty', True):
                monthly_summaries[month_str] = summary

        return {
            "year": year,
            "monthly_summaries": monthly_summaries
        }
