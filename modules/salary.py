# modules/salary.py
from typing import Dict, Any, List, Tuple
from core.models import SalaryConfig, OvertimeRecord


class SalaryModule:
    """加班工资计算模块"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._salary_config: SalaryConfig = None

    @property
    def salary_config(self) -> SalaryConfig:
        """获取工资配置（延迟加载）"""
        if self._salary_config is None:
            config_data = self.config_manager.get('overtime_pay', {})
            self._salary_config = SalaryConfig.from_dict(config_data)
        return self._salary_config

    def calculate(self, date: str, hours_str: str, day_type: str) -> str:
        """计算加班工资"""
        try:
            hours = float(hours_str)
            return self.salary_config.calculate(hours, day_type)
        except (ValueError, TypeError):
            return "0"

    def calculate_batch(
        self,
        records: List[OvertimeRecord]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """批量计算加班工资"""
        if not self.salary_config.enabled:
            return 0.0, []

        total_salary = 0.0
        details = []
        deduct_types = self.salary_config.deduct_types

        for record in records:
            if not self._should_calculate(record, deduct_types):
                continue

            rate = self._get_rate(record.day_type)
            try:
                hours = float(record.work_hours)
                if hours > 0:
                    salary = self.salary_config.hourly_wage * hours * rate
                    total_salary += salary
                    details.append({
                        'date': record.date,
                        'day_type': record.day_type,
                        'hours': record.work_hours,
                        'salary': f"{salary:.2f}元"
                    })
            except (ValueError, TypeError):
                continue

        return total_salary, details

    def _should_calculate(
        self,
        record: OvertimeRecord,
        deduct_types: List[str]
    ) -> bool:
        """检查是否应该计算加班工资"""
        if record.leave_type != "无":
            return record.leave_type in deduct_types
        return True

    def _get_rate(self, day_type: str) -> float:
        """获取倍率"""
        return self.salary_config._get_rate(day_type)

    def get_summary_text(self, summary: Dict[str, Any]) -> str:
        """获取加班工资汇总文本"""
        if not self.salary_config.enabled:
            return "加班工资计算未启用"

        month = summary.get('month', '')
        details = summary.get('details', {})

        lines = [
            f"【{month} 月加班工资汇总】",
            f"小时加班工资: {self.salary_config.hourly_wage}元/小时",
            ""
        ]

        total_salary = 0.0
        for day_type, data in details.items():
            if data['hours'] > 0:
                salary = self.calculate(
                    "2024-01-01",
                    str(data['hours']),
                    day_type
                )
                if salary != "0":
                    salary_val = float(salary.replace('元', ''))
                    total_salary += salary_val
                    lines.append(
                        f"  {day_type}: {data['hours']:.1f}小时 → {salary}"
                    )

        if total_salary > 0:
            lines.append(f"\n总计: {total_salary:.2f}元")
        else:
            lines.append("本月无加班工资")

        return "\n".join(lines)

    def reload_config(self):
        """重新加载配置"""
        self._salary_config = None
