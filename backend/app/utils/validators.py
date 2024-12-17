"""
数据验证工具类
用于处理考勤系统中的数据验证
"""

from datetime import datetime, time
from typing import Optional, Tuple, Dict, Any
import re

class AttendanceValidator:
    """考勤数据验证器"""
    
    @staticmethod
    def validate_datetime_format(date_str: str) -> Tuple[bool, str]:
        """
        验证日期时间格式
        支持的格式：
        1. YYYY-MM-DD
        2. YYYY-MM-DD HH:MM:SS
        
        Args:
            date_str: 日期时间字符串
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 尝试完整的日期时间格式
            datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return True, ''
        except ValueError:
            try:
                # 尝试仅日期格式
                datetime.strptime(date_str, '%Y-%m-%d')
                return True, ''
            except ValueError:
                return False, '日期时间格式无效，应为YYYY-MM-DD或YYYY-MM-DD HH:MM:SS'
    
    @staticmethod
    def validate_time_format(time_str: str) -> Tuple[bool, str]:
        """
        验证时间格式 (HH:MM:SS)
        
        Args:
            time_str: 时间字符串
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            datetime.strptime(time_str, '%H:%M:%S')
            return True, ''
        except ValueError:
            return False, '时间格式无效，应为HH:MM:SS'
    
    @staticmethod
    def validate_time_range(start_time: datetime, end_time: datetime) -> Tuple[bool, str]:
        """
        验证时间范围
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if start_time >= end_time:
            return False, '开始时间必须早于结束时间'
        return True, ''
    
    @staticmethod
    def validate_attendance_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证考勤记录数据
        
        Args:
            data: 考勤数据字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        required_fields = ['employee_id', 'date']
        for field in required_fields:
            if field not in data:
                return False, f'缺少必填字段: {field}'
        
        # 验证日期格式
        if 'date' in data:
            is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['date'])
            if not is_valid:
                return False, error_msg
        
        # 验证打卡时间格式
        if 'check_in' in data:
            is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['check_in'])
            if not is_valid:
                return False, error_msg
                
        if 'check_out' in data:
            is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['check_out'])
            if not is_valid:
                return False, error_msg
        
        return True, ''
    
    @staticmethod
    def validate_leave_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证请假申请数据
        
        Args:
            data: 请假数据字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        required_fields = ['employee_id', 'leave_type', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return False, f'缺少必填字段: {field}'
        
        # 验证请假类型
        valid_leave_types = ['sick', 'annual', 'personal', 'other']
        if data['leave_type'] not in valid_leave_types:
            return False, f'无效的请假类型，有效值为: {", ".join(valid_leave_types)}'
        
        # 验证日期格式和范围
        is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['start_date'])
        if not is_valid:
            return False, error_msg
            
        is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['end_date'])
        if not is_valid:
            return False, error_msg
            
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')
        is_valid, error_msg = AttendanceValidator.validate_time_range(start_date, end_date)
        if not is_valid:
            return False, error_msg
            
        return True, ''
    
    @staticmethod
    def validate_overtime_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证加班申请数据
        
        Args:
            data: 加班数据字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        required_fields = ['employee_id', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return False, f'缺少必填字段: {field}'
        
        # 验证时间格式和范围
        is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['start_time'])
        if not is_valid:
            return False, error_msg
            
        is_valid, error_msg = AttendanceValidator.validate_datetime_format(data['end_time'])
        if not is_valid:
            return False, error_msg
            
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
        is_valid, error_msg = AttendanceValidator.validate_time_range(start_time, end_time)
        if not is_valid:
            return False, error_msg
            
        return True, ''
    
    @staticmethod
    def validate_attendance_rule_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证考勤规则数据
        
        Args:
            data: 考勤规则数据字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        required_fields = ['name', 'work_start_time', 'work_end_time']
        for field in required_fields:
            if field not in data:
                return False, f'缺少必填字段: {field}'
        
        # 验证时间格式
        is_valid, error_msg = AttendanceValidator.validate_time_format(data['work_start_time'])
        if not is_valid:
            return False, error_msg
            
        is_valid, error_msg = AttendanceValidator.validate_time_format(data['work_end_time'])
        if not is_valid:
            return False, error_msg
            
        # 验证阈值
        if 'late_threshold' in data and not isinstance(data['late_threshold'], int):
            return False, 'late_threshold必须是整数'
            
        if 'early_leave_threshold' in data and not isinstance(data['early_leave_threshold'], int):
            return False, 'early_leave_threshold必须是整数'
            
        if 'overtime_minimum' in data and not isinstance(data['overtime_minimum'], int):
            return False, 'overtime_minimum必须是整数'
            
        return True, ''
