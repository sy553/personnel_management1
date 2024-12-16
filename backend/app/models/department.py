from datetime import datetime
from app import db
from sqlalchemy import ForeignKey

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    parent_id = db.Column(db.Integer, ForeignKey('departments.id', name='fk_department_parent', use_alter=True), nullable=True)
    manager_id = db.Column(db.Integer, ForeignKey('employees.id', name='fk_department_manager', use_alter=True), nullable=True)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    parent = db.relationship('Department', remote_side=[id], backref=db.backref('children', lazy='dynamic'), post_update=True)
    manager = db.relationship('Employee', foreign_keys=[manager_id], backref=db.backref('managed_departments', lazy='dynamic'), post_update=True)
    positions = db.relationship('Position', back_populates='department', lazy='dynamic')
    employees = db.relationship('Employee', foreign_keys='Employee.department_id', back_populates='department', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.name}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'manager_id': self.manager_id,
            'manager_name': self.manager.name if self.manager else None,
            'level': self.level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
