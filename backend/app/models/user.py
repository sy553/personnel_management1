from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户表 - 存储系统用户信息"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(255), nullable=False, comment='密码')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='邮箱')
    role = db.Column(db.String(20), nullable=False, default='employee', comment='角色(admin/manager/employee)')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 添加与员工的关联
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), comment='关联的员工ID')
    employee = db.relationship(
        'Employee',
        foreign_keys=[employee_id],
        back_populates='user_account'  # 使用更具体的名称
    )
    
    # 重置密码相关字段
    reset_code = db.Column(db.String(6), comment='重置密码验证码')
    reset_code_expires = db.Column(db.DateTime, comment='重置码过期时间')
    
    # 登录尝试相关字段
    login_attempts = db.Column(db.Integer, default=0, comment='登录失败尝试次数')
    last_failed_login = db.Column(db.DateTime, comment='最后一次登录失败时间')
    account_locked_until = db.Column(db.DateTime, comment='账户锁定截止时间')

    def set_password(self, password):
        """设置密码"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'employee_id': self.employee.id if self.employee else None,  
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
