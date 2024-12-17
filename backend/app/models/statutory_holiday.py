"""
法定节假日管理模型
"""
from datetime import datetime
from app import db

class StatutoryHoliday(db.Model):
    """法定节假日模型"""
    __tablename__ = 'statutory_holidays'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='节假日名称')
    date = db.Column(db.Date, nullable=False, comment='节假日日期')
    holiday_type = db.Column(db.String(20), nullable=False, comment='类型(holiday:节假日/workday:调休工作日)')
    year = db.Column(db.Integer, nullable=False, comment='年份')
    description = db.Column(db.String(200), comment='描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StatutoryHoliday {self.name} {self.date}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.strftime('%Y-%m-%d'),
            'holiday_type': self.holiday_type,
            'year': self.year,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
