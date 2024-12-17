# 导入所有模型
from .user import User
from .employee import Employee, EducationHistory, WorkHistory
from .department import Department
from .position import Position
from .salary import SalaryStructure, SalaryRecord
from .attendance import Attendance, Leave
from .salary_structure_assignment import SalaryStructureAssignment
from .statutory_holiday import StatutoryHoliday

__all__ = [
    'User',
    'Employee',
    'Department',
    'Position',
    'SalaryStructure',
    'SalaryRecord',
    'Attendance',
    'Leave',
    'EducationHistory',
    'WorkHistory',
    'SalaryStructureAssignment',
    'StatutoryHoliday'
]
