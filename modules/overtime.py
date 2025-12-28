# modules/overtime.py
from datetime import datetime
from typing import Dict, Any

class OvertimeModule:
    """加班统计模块"""

    def __init__(self, data_manager, holiday_checker, config_manager):
        self.data_manager = data_manager
        self.holiday_checker = holiday_checker
        self.config_manager = config_manager

    def get_monthly_summary(self, month: str = None) -> Dict[str, Any]:
        """获取月度汇总统计"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        records = self.data_manager.get_monthly_records(month)
        if not records:
            return {"month": month, "total_hours": 0, "details": {}, "empty": True}

        summary = {
            '工作日': {'hours': 0, 'count': 0},
            '休息日': {'hours': 0, 'count': 0},
            '节假日': {'hours': 0, 'count': 0},
            '调休日': {'hours': 0, 'count': 0},
            '请假': {'hours': 0, 'count': 0}
        }

        for record in records:
            if len(record) < 4:
                continue

            day_type = record[2]
            hours_str = record[3]
            leave_type = record[4] if len(record) > 4 else "无"

            try:
                hours = float(hours_str) if hours_str != "无" else 0
            except:
                hours = 0

            if leave_type != "无":
                summary['请假']['hours'] += abs(hours)
                summary['请假']['count'] += 1
            elif day_type in summary:
                summary[day_type]['hours'] += hours
                summary[day_type]['count'] += 1

        total_hours = sum([v['hours'] for v in summary.values()])

        return {
            "month": month,
            "total_hours": total_hours,
            "details": summary,
            "empty": False
        }

    def submit_overtime(self, data: Dict[str, Any]) -> tuple:
        """提交加班记录"""
        # 验证数据
        if not data.get('user') or not data.get('date') or not data.get('day_type'):
            raise Exception("缺少必填字段")

        # 自动验证日期类型
        if self.holiday_checker:
            detected_type, reason = self.holiday_checker.get_day_type(data['date'])
            if detected_type != data['day_type'] and not data.get('is_leave'):
                print(f"⚠️ 类型不匹配: {data['date']} 检测到 {detected_type}({reason})，用户选择 {data['day_type']}")

        # 构建记录
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 加班工资计算
        salary = "0"
        if data.get('calculate_salary', False):
            salary = data['salary']

        if data.get('is_leave'):
            leave_type = data.get('leave_type', '')
            day_type = "休息日" if leave_type == "事假" else data.get('day_type', '工作日')
            work_hours = data.get('leave_hours', '0') if leave_type == "事假" else "0"

            record = [data['date'], data['user'], day_type, work_hours, leave_type,
                     "事假" if leave_type == "事假" else "无", timestamp, salary]
        else:
            record = [data['date'], data['user'], data['day_type'], data.get('work_hours', '0'),
                     "无", "无", timestamp, salary]

        # 保存记录
        if self.data_manager.add_record(record):
            return True, "记录已保存", record
        else:
            return False, "保存失败", None
