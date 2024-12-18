from datetime import datetime
from sqlalchemy import and_, or_
from app import db
from app.models.attendance import AttendanceRule, Attendance
from app.models.employee import Employee
from app.models.department import Department

class AttendanceService:
    @staticmethod
    def get_attendance_rules(department_id=None):
        """获取考勤规则列表
        
        Args:
            department_id: 部门ID，如果提供则只返回该部门的规则
            
        Returns:
            list: 考勤规则列表
        """
        query = AttendanceRule.query
        if department_id:
            query = query.filter_by(department_id=department_id)
        return query.order_by(AttendanceRule.priority.desc()).all()

    @staticmethod
    def get_attendance_rule(rule_id):
        """获取单个考勤规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            AttendanceRule: 考勤规则对象
        """
        return AttendanceRule.query.get(rule_id)

    @staticmethod
    def create_attendance_rule(rule_data):
        """创建考勤规则
        
        Args:
            rule_data: 规则数据字典
            
        Returns:
            AttendanceRule: 创建的考勤规则对象
        """
        rule = AttendanceRule(**rule_data)
        db.session.add(rule)
        db.session.commit()
        return rule

    @staticmethod
    def update_attendance_rule(rule_id, rule_data):
        """更新考勤规则
        
        Args:
            rule_id: 规则ID
            rule_data: 规则数据字典
            
        Returns:
            AttendanceRule: 更新后的考勤规则对象
        """
        rule = AttendanceRule.query.get(rule_id)
        if rule:
            for key, value in rule_data.items():
                setattr(rule, key, value)
            db.session.commit()
        return rule

    @staticmethod
    def delete_attendance_rule(rule_id):
        """删除考勤规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 是否删除成功
        """
        rule = AttendanceRule.query.get(rule_id)
        if rule:
            db.session.delete(rule)
            db.session.commit()
            return True
        return False

    @staticmethod
    def assign_rule_to_department(rule_id, department_id):
        """将考勤规则分配给部门
        
        Args:
            rule_id: 规则ID
            department_id: 部门ID
            
        Returns:
            bool: 是否分配成功
        """
        rule = AttendanceRule.query.get(rule_id)
        department = Department.query.get(department_id)
        
        if not rule or not department:
            return False
            
        rule.department_id = department_id
        db.session.commit()
        return True

    @staticmethod
    def assign_rule_to_employees(rule_id, employee_ids):
        """将考勤规则分配给指定员工
        
        Args:
            rule_id: 规则ID
            employee_ids: 员工ID列表
            
        Returns:
            bool: 是否分配成功
        """
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return False
            
        employees = Employee.query.filter(Employee.id.in_(employee_ids)).all()
        if not employees:
            return False
            
        # 清除这些员工之前的规则分配（如果有）
        for employee in employees:
            employee.attendance_rules = []
            
        # 分配新规则
        for employee in employees:
            employee.attendance_rules.append(rule)
            
        db.session.commit()
        return True

    @staticmethod
    def get_employee_rules(employee_id):
        """获取员工的所有考勤规则
        
        Args:
            employee_id: 员工ID
            
        Returns:
            list: 考勤规则列表
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return []
            
        # 获取员工直接分配的规则
        direct_rules = employee.attendance_rules.all()
        
        # 获取员工所在部门的规则
        dept_rules = []
        if employee.department_id:
            dept_rules = AttendanceRule.query.filter_by(
                department_id=employee.department_id
            ).all()
            
        # 合并规则并按优先级排序
        all_rules = list(set(direct_rules + dept_rules))
        return sorted(all_rules, key=lambda x: x.priority, reverse=True)

    @staticmethod
    def get_active_rule_for_employee(employee_id, check_date):
        """获取员工在指定日期的有效考勤规则
        
        Args:
            employee_id: 员工ID
            check_date: 检查日期
            
        Returns:
            AttendanceRule: 有效的考勤规则
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return None
            
        # 获取所有适用的规则
        all_rules = AttendanceService.get_employee_rules(employee_id)
        
        # 按优先级筛选出当前日期有效的规则
        valid_rules = [rule for rule in all_rules if rule.is_valid_for_date(check_date)]
        
        # 返回优先级最高的规则
        return valid_rules[0] if valid_rules else None
