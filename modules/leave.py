# modules/leave.py
from typing import Dict, Any

class LeaveModule:
    """请假管理模块"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def get_leave_types(self) -> list:
        """获取请假类型列表"""
        return self.config_manager.get('leave_types', ['事假', '病假', '年假', '婚假', '产假'])

    def should_deduct_hours(self, leave_type: str) -> bool:
        """检查指定请假类型是否扣除工时"""
        deduct_types = self.config_manager.get('overtime_pay.deduct_types', ['事假'])
        return leave_type in deduct_types

    def process_leave(self, data: Dict[str, Any]) -> tuple:
        """处理请假数据"""
        leave_type = data.get('leave_type', '')
        if not leave_type:
            raise Exception("请选择请假类型")

        leave_types = self.get_leave_types()
        if leave_type not in leave_types:
            raise Exception(f"无效的请假类型: {leave_type}")

        # 检查该类型是否需要扣除工时
        should_deduct = self.should_deduct_hours(leave_type)

        if leave_type == "事假":
            if not data.get('leave_hours'):
                raise Exception("事假必须选择时长")

            if should_deduct:
                day_type = "休息日"
                work_hours = data.get('leave_hours', '0')
            else:
                day_type = data.get('day_type', '工作日')
                work_hours = "0"
        else:
            # 其他请假类型
            if should_deduct:
                # 如果配置了扣除，则按休息日处理
                day_type = "休息日"
                work_hours = "-4"  # 默认半天
            else:
                day_type = data.get('day_type', '工作日')
                work_hours = "0"

        return {
            'day_type': day_type,
            'work_hours': work_hours,
            'leave_type': leave_type,
            'leave_hours': data.get('leave_hours', '0')
        }
