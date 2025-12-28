# modules/salary.py
from typing import Dict, Any

class SalaryModule:
    """加班工资计算模块"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def calculate(self, date: str, hours_str: str, day_type: str) -> str:
        """计算加班工资"""
        overtime_pay = self.config_manager.get('overtime_pay', {})
        if not overtime_pay.get('enabled', False):
            return "0"

        try:
            hours = float(hours_str)
            if hours <= 0:
                return "0"

            # 获取小时加班工资
            hourly_wage = overtime_pay.get('hourly_wage', 50.0)

            # 获取倍率
            rate = 0
            if day_type == "工作日":
                rate = overtime_pay.get('weekday_rate', 1.5)
            elif day_type == "休息日":
                rate = overtime_pay.get('weekend_rate', 2.0)
            elif day_type == "节假日":
                rate = overtime_pay.get('holiday_rate', 3.0)
            elif day_type == "调休日":
                rate = 1.5

            # 计算：小时加班工资 × 时长 × 倍率
            salary = hourly_wage * hours * rate
            return f"{salary:.2f}元"
        except:
            return "0"

    def calculate_batch(self, records: list) -> tuple:
        """批量计算加班工资"""
        total_salary = 0
        details = []

        overtime_pay = self.config_manager.get('overtime_pay', {})
        if not overtime_pay.get('enabled', False):
            return 0, []

        hourly_wage = overtime_pay.get('hourly_wage', 50.0)
        deduct_types = overtime_pay.get('deduct_types', ['事假'])

        for record in records:
            if len(record) < 4:
                continue

            date = record[0]
            day_type = record[2]
            hours_str = record[3]
            leave_type = record[4] if len(record) > 4 else "无"

            # 检查是否需要计算加班工资
            if leave_type != "无":
                if leave_type not in deduct_types:
                    continue

            # 获取倍率
            rate = 0
            if day_type == "工作日":
                rate = overtime_pay.get('weekday_rate', 1.5)
            elif day_type == "休息日":
                rate = overtime_pay.get('weekend_rate', 2.0)
            elif day_type == "节假日":
                rate = overtime_pay.get('holiday_rate', 3.0)
            elif day_type == "调休日":
                rate = 1.5

            try:
                hours = float(hours_str)
                if hours > 0:
                    salary = hourly_wage * hours * rate
                    total_salary += salary
                    details.append({
                        'date': date,
                        'day_type': day_type,
                        'hours': hours_str,
                        'salary': f"{salary:.2f}元"
                    })
            except:
                pass

        return total_salary, details

    def get_summary_text(self, summary: Dict[str, Any]) -> str:
        """获取加班工资汇总文本"""
        if not self.config_manager.get('overtime_pay.enabled', False):
            return "加班工资计算未启用"

        month = summary.get('month', '')
        details = summary.get('details', {})
        hourly_wage = self.config_manager.get('overtime_pay.hourly_wage', 50.0)

        text = f"【{month} 月加班工资汇总】\n"
        text += f"小时加班工资: {hourly_wage}元/小时\n\n"

        total_salary = 0
        for day_type, data in details.items():
            if data['hours'] > 0:
                salary = self.calculate("2024-01-01", str(data['hours']), day_type)
                if salary != "0":
                    salary_val = float(salary.replace('元', ''))
                    total_salary += salary_val
                    text += f"  {day_type}: {data['hours']:.1f}小时 → {salary}\n"

        if total_salary > 0:
            text += f"\n总计: {total_salary:.2f}元"
        else:
            text += "本月无加班工资"

        return text
