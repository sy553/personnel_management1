"""
假期管理相关模型
"""
from datetime import datetime
from app.extensions import db

class HolidayType(db.Model):
    """假期类型模型"""
    __tablename__ = 'holiday_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='假期类型名称')
    code = db.Column(db.String(20), nullable=False, unique=True, comment='假期类型代码')
    annual_quota = db.Column(db.Float, nullable=True, comment='年度配额（天）')
    min_duration = db.Column(db.Float, nullable=True, comment='最小请假时长（天）')
    max_duration = db.Column(db.Float, nullable=True, comment='最大请假时长（天）')
    requires_proof = db.Column(db.Boolean, default=False, comment='是否需要证明材料')
    description = db.Column(db.String(200), nullable=True, comment='描述')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    holiday_requests = db.relationship('HolidayRequest', back_populates='holiday_type', lazy='dynamic')
    holiday_balances = db.relationship('HolidayBalance', back_populates='holiday_type', lazy='dynamic')

    def __repr__(self):
        return f'<HolidayType {self.name}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'annual_quota': self.annual_quota,
            'min_duration': self.min_duration,
            'max_duration': self.max_duration,
            'requires_proof': self.requires_proof,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class HolidayRequest(db.Model):
    """假期申请模型"""
    __tablename__ = 'holiday_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    holiday_type_id = db.Column(db.Integer, db.ForeignKey('holiday_types.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, comment='开始日期')
    end_date = db.Column(db.Date, nullable=False, comment='结束日期')
    duration = db.Column(db.Float, nullable=False, comment='请假天数')
    reason = db.Column(db.String(500), nullable=False, comment='请假原因')
    proof_url = db.Column(db.String(255), nullable=True, comment='证明材料URL')
    status = db.Column(db.String(20), nullable=False, default='pending', comment='状态：pending-待审批，approved-已批准，rejected-已拒绝，cancelled-已取消')
    approver_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    approval_comment = db.Column(db.String(500), nullable=True, comment='审批意见')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref=db.backref('holiday_requests', lazy='dynamic'))
    holiday_type = db.relationship('HolidayType', back_populates='holiday_requests')
    approver = db.relationship('Employee', foreign_keys=[approver_id], backref=db.backref('approved_holiday_requests', lazy='dynamic'))

    def __repr__(self):
        return f'<HolidayRequest {self.employee.name} - {self.holiday_type.name}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee': self.employee.to_dict() if self.employee else None,
            'holiday_type': self.holiday_type.to_dict() if self.holiday_type else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration': self.duration,
            'reason': self.reason,
            'proof_url': self.proof_url,
            'status': self.status,
            'approver': self.approver.to_dict() if self.approver else None,
            'approval_time': self.approval_time.isoformat() if self.approval_time else None,
            'approval_comment': self.approval_comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class HolidayBalance(db.Model):
    """假期余额模型"""
    __tablename__ = 'holiday_balances'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    holiday_type_id = db.Column(db.Integer, db.ForeignKey('holiday_types.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False, comment='年份')
    total_days = db.Column(db.Float, nullable=False, default=0, comment='总天数')
    used_days = db.Column(db.Float, nullable=False, default=0, comment='已使用天数')
    remaining_days = db.Column(db.Float, nullable=False, default=0, comment='剩余天数')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    employee = db.relationship('Employee', backref=db.backref('holiday_balances', lazy='dynamic'))
    holiday_type = db.relationship('HolidayType', back_populates='holiday_balances')

    def __repr__(self):
        return f'<HolidayBalance {self.employee.name} - {self.holiday_type.name} ({self.year})>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee': self.employee.to_dict() if self.employee else None,
            'holiday_type': self.holiday_type.to_dict() if self.holiday_type else None,
            'year': self.year,
            'total_days': self.total_days,
            'used_days': self.used_days,
            'remaining_days': self.remaining_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
