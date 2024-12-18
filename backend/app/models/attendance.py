from app import db
from datetime import datetime

class Attendance(db.Model):
    """考勤记录表"""
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, comment='员工ID')
    date = db.Column(db.Date, nullable=False, comment='考勤日期')
    check_in = db.Column(db.DateTime, comment='上班打卡时间')
    check_out = db.Column(db.DateTime, comment='下班打卡时间')
    status = db.Column(db.String(20), comment='考勤状态(normal/late/early/absent)')
    remark = db.Column(db.String(200), comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    employee = db.relationship('Employee', backref=db.backref('attendances', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'date': self.date.strftime('%Y-%m-%d'),
            'check_in': self.check_in.strftime('%Y-%m-%d %H:%M:%S') if self.check_in else None,
            'check_out': self.check_out.strftime('%Y-%m-%d %H:%M:%S') if self.check_out else None,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Leave(db.Model):
    """请假记录表"""
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, comment='员工ID')
    leave_type = db.Column(db.String(20), nullable=False, comment='请假类型(sick/annual/personal/other)')
    start_date = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_date = db.Column(db.DateTime, nullable=False, comment='结束时间')
    reason = db.Column(db.String(200), comment='请假原因')
    status = db.Column(db.String(20), default='pending', comment='状态(pending/approved/rejected)')
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.id'), comment='审批人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref=db.backref('leaves', lazy='dynamic'))
    approver = db.relationship('Employee', foreign_keys=[approved_by], backref=db.backref('approved_leaves', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'leave_type': self.leave_type,
            'start_date': self.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': self.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.name if self.approver else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Overtime(db.Model):
    """加班记录表"""
    __tablename__ = 'overtimes'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, comment='员工ID')
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='结束时间')
    reason = db.Column(db.String(200), comment='加班原因')
    status = db.Column(db.String(20), default='pending', comment='状态(pending/approved/rejected)')
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.id'), comment='审批人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref=db.backref('overtimes', lazy='dynamic'))
    approver = db.relationship('Employee', foreign_keys=[approved_by], backref=db.backref('approved_overtimes', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.name if self.approver else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 考勤规则与员工关联表
employee_attendance_rules = db.Table('employee_attendance_rules',
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True, comment='员工ID'),
    db.Column('rule_id', db.Integer, db.ForeignKey('attendance_rules.id'), primary_key=True, comment='考勤规则ID'),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, comment='创建时间')
)

class AttendanceRule(db.Model):
    """考勤规则配置表"""
    __tablename__ = 'attendance_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='规则名称')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), comment='适用部门ID')
    work_start_time = db.Column(db.Time, nullable=False, comment='上班时间')
    work_end_time = db.Column(db.Time, nullable=False, comment='下班时间')
    late_threshold = db.Column(db.Integer, default=15, comment='迟到阈值(分钟)')
    early_leave_threshold = db.Column(db.Integer, default=15, comment='早退阈值(分钟)')
    overtime_minimum = db.Column(db.Integer, default=60, comment='最小加班时长(分钟)')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认规则')
    description = db.Column(db.String(200), comment='规则说明')
    
    # 新增字段
    priority = db.Column(db.Integer, nullable=True, default=0, comment='规则优先级，数字越大优先级越高')
    rule_type = db.Column(db.String(20), nullable=True, default='regular', comment='规则类型(regular/special/temporary)')
    effective_start_date = db.Column(db.Date, nullable=False, comment='生效开始日期')
    effective_end_date = db.Column(db.Date, nullable=True, comment='生效结束日期')
    flexible_time = db.Column(db.Integer, default=30, comment='弹性工作时间(分钟)')
    break_start_time = db.Column(db.Time, nullable=True, comment='休息开始时间')
    break_end_time = db.Column(db.Time, nullable=True, comment='休息结束时间')
    overtime_rate = db.Column(db.Float, default=1.5, comment='加班工资倍率')
    weekend_overtime_rate = db.Column(db.Float, default=2.0, comment='周末加班工资倍率')
    holiday_overtime_rate = db.Column(db.Float, default=3.0, comment='节假日加班工资倍率')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    department = db.relationship('Department', backref=db.backref('attendance_rules', lazy='dynamic'))
    # 添加与员工的多对多关系
    employees = db.relationship('Employee', secondary=employee_attendance_rules, 
                              backref=db.backref('attendance_rules', lazy='dynamic'))

    def is_valid_for_date(self, check_date):
        """检查规则在指定日期是否有效
        
        Args:
            check_date: 要检查的日期
            
        Returns:
            bool: 规则是否有效
        """
        if not self.effective_start_date:
            return False
            
        if check_date < self.effective_start_date:
            return False
            
        if self.effective_end_date and check_date > self.effective_end_date:
            return False
            
        return True
        
    def has_conflict_with(self, other_rule):
        """检查是否与其他规则存在冲突
        
        Args:
            other_rule: 要检查的其他规则
            
        Returns:
            bool: 是否存在冲突
        """
        # 如果部门不同，则不冲突
        if self.department_id != other_rule.department_id:
            return False
            
        # 检查时间段是否重叠
        if self.effective_end_date and other_rule.effective_start_date:
            if self.effective_end_date < other_rule.effective_start_date:
                return False
                
        if other_rule.effective_end_date and self.effective_start_date:
            if other_rule.effective_end_date < self.effective_start_date:
                return False
                
        return True
        
    @staticmethod
    def get_active_rule(department_id, check_date):
        """获取指定部门在指定日期的有效规则
        
        Args:
            department_id: 部门ID
            check_date: 检查日期
            
        Returns:
            AttendanceRule: 有效的考勤规则
        """
        # 首先查找部门特定的规则
        if department_id:
            dept_rules = AttendanceRule.query.filter(
                db.and_(
                    AttendanceRule.department_id == department_id,
                    AttendanceRule.effective_start_date <= check_date,
                    db.or_(
                        AttendanceRule.effective_end_date >= check_date,
                        AttendanceRule.effective_end_date.is_(None)
                    )
                )
            ).order_by(AttendanceRule.priority.desc()).first()
            
            if dept_rules:
                return dept_rules
                
        # 如果没有部门特定的规则，返回默认规则
        return AttendanceRule.query.filter(
            db.and_(
                AttendanceRule.is_default == True,
                AttendanceRule.effective_start_date <= check_date,
                db.or_(
                    AttendanceRule.effective_end_date >= check_date,
                    AttendanceRule.effective_end_date.is_(None)
                )
            )
        ).first()

    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 规则信息字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'work_start_time': self.work_start_time.strftime('%H:%M') if self.work_start_time else None,
            'work_end_time': self.work_end_time.strftime('%H:%M') if self.work_end_time else None,
            'break_start_time': self.break_start_time.strftime('%H:%M') if self.break_start_time else None,
            'break_end_time': self.break_end_time.strftime('%H:%M') if self.break_end_time else None,
            'late_threshold': self.late_threshold,
            'early_leave_threshold': self.early_leave_threshold,
            'overtime_minimum': self.overtime_minimum,
            'is_default': self.is_default,
            'description': self.description,
            'priority': self.priority,
            'rule_type': self.rule_type,
            'effective_start_date': self.effective_start_date.strftime('%Y-%m-%d') if self.effective_start_date else None,
            'effective_end_date': self.effective_end_date.strftime('%Y-%m-%d') if self.effective_end_date else None,
            'flexible_time': self.flexible_time,
            'overtime_rate': self.overtime_rate,
            'weekend_overtime_rate': self.weekend_overtime_rate,
            'holiday_overtime_rate': self.holiday_overtime_rate,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class AttendanceLocation(db.Model):
    """打卡地点表"""
    __tablename__ = 'attendance_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='地点名称')
    address = db.Column(db.String(200), nullable=False, comment='详细地址')
    latitude = db.Column(db.Float, nullable=False, comment='纬度')
    longitude = db.Column(db.Float, nullable=False, comment='经度')
    radius = db.Column(db.Integer, default=100, comment='打卡范围(米)')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
