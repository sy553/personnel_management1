from datetime import datetime
from app import db
from sqlalchemy import ForeignKey

class Position(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    department_id = db.Column(db.Integer, ForeignKey('departments.id', name='fk_position_department'), nullable=False)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    department = db.relationship('Department', back_populates='positions')
    employees = db.relationship('Employee', back_populates='position', lazy='dynamic')

    def __repr__(self):
        return f'<Position {self.name}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'level': self.level
        }
