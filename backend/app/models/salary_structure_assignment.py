from app import db
from datetime import datetime

class SalaryStructureAssignment(db.Model):
    """工资结构分配表"""
    __tablename__ = 'salary_structure_assignments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    salary_structure_id = db.Column(db.Integer, db.ForeignKey('salary_structures.id'), nullable=False, comment='工资结构ID')
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, comment='员工ID')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True, comment='部门ID')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认工资结构')
    effective_date = db.Column(db.Date, nullable=False, comment='生效日期')
    expiry_date = db.Column(db.Date, nullable=True, comment='失效日期')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    salary_structure = db.relationship('SalaryStructure', backref=db.backref('assignments', lazy=True))
    employee = db.relationship('Employee', backref=db.backref('salary_assignments', lazy=True), foreign_keys=[employee_id])
    department = db.relationship('Department', backref=db.backref('salary_assignments', lazy=True), foreign_keys=[department_id])
    
    def __repr__(self):
        return f'<SalaryStructureAssignment {self.id}>'
        
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'salary_structure_id': self.salary_structure_id,
            'employee_id': self.employee_id,
            'department_id': self.department_id,
            'is_default': self.is_default,
            'effective_date': self.effective_date.strftime('%Y-%m-%d') if self.effective_date else None,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'salary_structure': self.salary_structure.to_dict() if self.salary_structure else None,
            'employee': {
                'id': self.employee.id,
                'name': self.employee.name
            } if self.employee else None,
            'department': {
                'id': self.department.id,
                'name': self.department.name
            } if self.department else None
        }
