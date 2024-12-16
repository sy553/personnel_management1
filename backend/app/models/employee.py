from app import db
from datetime import datetime
from sqlalchemy import ForeignKey
from .department import Department
from .position import Position

class Employee(db.Model):
    """员工表"""
    __tablename__ = 'employees'  # 修改表名为实际的表名
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id', name='fk_employee_user'), nullable=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    education = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    id_card = db.Column(db.String(18))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    hire_date = db.Column(db.Date)
    resignation_date = db.Column(db.Date)  # 添加离职日期字段
    department_id = db.Column(db.Integer, ForeignKey('departments.id', name='fk_employee_department'))
    position_id = db.Column(db.Integer, ForeignKey('positions.id', name='fk_employee_position'))
    employment_status = db.Column(db.String(20), default='active', nullable=False)
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('employee', uselist=False))
    department = db.relationship('Department', foreign_keys=[department_id], back_populates='employees')
    position = db.relationship('Position', foreign_keys=[position_id], back_populates='employees')
    education_history = db.relationship('EducationHistory', back_populates='employee', lazy='dynamic')
    work_history = db.relationship('WorkHistory', back_populates='employee', lazy='dynamic')
    contract_attachments = db.relationship('ContractAttachment', back_populates='employee', lazy='dynamic')
    position_changes = db.relationship('PositionChangeHistory', back_populates='employee', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Employee, self).__init__(**kwargs)
        if self.employment_status is None:
            self.employment_status = 'active'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'name': self.name,
            'gender': self.gender,
            'education': self.education,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'id_card': self.id_card,
            'phone': self.phone,
            'address': self.address,
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'resignation_date': self.resignation_date.strftime('%Y-%m-%d') if self.resignation_date else None,
            'department_id': self.department_id,  # 添加部门ID
            'department': self.department.name if self.department else None,
            'position_id': self.position_id,  # 添加职位ID
            'position': self.position.name if self.position else None,
            'employment_status': self.employment_status,
            'photo_url': self.photo_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class EducationHistory(db.Model):
    """教育经历表"""
    __tablename__ = 'education_history'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)  # 修改外键引用
    school = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100))
    degree = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', back_populates='education_history')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'school': self.school,
            'major': self.major,
            'degree': self.degree,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class WorkHistory(db.Model):
    """工作经历表"""
    __tablename__ = 'work_history'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)  # 修改外键引用
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', back_populates='work_history')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'company': self.company,
            'position': self.position,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class ContractAttachment(db.Model):
    """合同附件表"""
    __tablename__ = 'contract_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)  # 修改外键引用
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', back_populates='contract_attachments')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class PositionChangeHistory(db.Model):
    """职位变更历史表"""
    __tablename__ = 'position_change_history'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)  # 修改外键引用
    old_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    new_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    old_position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))
    new_position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    change_date = db.Column(db.Date, nullable=False)
    change_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', back_populates='position_changes')
    old_department = db.relationship('Department', foreign_keys=[old_department_id])
    new_department = db.relationship('Department', foreign_keys=[new_department_id])
    old_position = db.relationship('Position', foreign_keys=[old_position_id])
    new_position = db.relationship('Position', foreign_keys=[new_position_id])

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'old_department': self.old_department.name if self.old_department else None,
            'new_department': self.new_department.name,
            'old_position': self.old_position.name if self.old_position else None,
            'new_position': self.new_position.name,
            'change_date': self.change_date.strftime('%Y-%m-%d'),
            'change_reason': self.change_reason,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
