from app import db
from datetime import datetime

class AttendanceLocation(db.Model):
    """考勤打卡地点表"""
    __tablename__ = 'attendance_locations'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='地点名称')
    address = db.Column(db.String(255), nullable=False, comment='详细地址')
    latitude = db.Column(db.Float, nullable=False, comment='纬度')
    longitude = db.Column(db.Float, nullable=False, comment='经度')
    radius = db.Column(db.Integer, nullable=False, default=100, comment='打卡范围(米)')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
