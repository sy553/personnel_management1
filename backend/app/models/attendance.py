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