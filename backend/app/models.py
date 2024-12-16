from datetime import datetime
from app import db, bcrypt

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, manager, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 登录尝试相关字段
    login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    account_locked_until = db.Column(db.DateTime)

    def set_password(self, password):
        """设置密码"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """验证密码"""
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'role': self.role,
                'is_active': self.is_active,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
            }
        except Exception as e:
            print(f"转换用户数据错误: user_id={self.id}, error={str(e)}")
            return None

class Employee(db.Model):
    """员工模型"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_employee_user', deferrable=True), nullable=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)  # 工号
    name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    id_card = db.Column(db.String(18), unique=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    
    # 工作信息
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', name='fk_employee_department', deferrable=True))
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id', name='fk_employee_position', deferrable=True))
    hire_date = db.Column(db.Date)
    employment_status = db.Column(db.String(20), default='active')  # active, resigned, suspended
    
    # 系统信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标志

    # 关联关系
    department = db.relationship('Department', backref=db.backref('employees', lazy=True))
    position = db.relationship('Position', backref=db.backref('employees', lazy=True))
    education_history = db.relationship('EducationHistory', backref='employee', lazy=True, cascade='all, delete-orphan')
    work_history = db.relationship('WorkHistory', backref='employee', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='employee', lazy=True)

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                'id': self.id,
                'user_id': self.user_id,
                'employee_id': self.employee_id,
                'name': self.name,
                'gender': self.gender,
                'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
                'id_card': self.id_card,
                'phone': self.phone,
                'email': self.email,
                'address': self.address,
                'department_id': self.department_id,
                'department_name': self.department.name if self.department else None,
                'position_id': self.position_id,
                'position_name': self.position.name if self.position else None,
                'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
                'employment_status': self.employment_status,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
            }
        except Exception as e:
            print(f"Error in to_dict: {str(e)}")
            return {}

class EducationHistory(db.Model):
    """教育经历模型"""
    __tablename__ = 'education_history'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'))
    school = db.Column(db.String(100))
    major = db.Column(db.String(100))
    degree = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'school': self.school,
            'major': self.major,
            'degree': self.degree,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class WorkHistory(db.Model):
    """工作经历模型"""
    __tablename__ = 'work_history'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'company': self.company,
            'position': self.position,
            'description': self.description,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Department(db.Model):
    """部门模型"""
    __tablename__ = 'departments'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='部门名称')
    description = db.Column(db.String(200), comment='部门描述')
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id', name='fk_department_parent', deferrable=True))
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id', name='fk_department_manager', deferrable=True))
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'parent_id': self.parent_id,
                'manager_id': self.manager_id,
                'status': self.status,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
            }
        except Exception as e:
            print(f"转换部门数据错误: department_id={self.id}, error={str(e)}")
            return None

class Position(db.Model):
    """职位模型"""
    __tablename__ = 'positions'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', name='fk_position_department', deferrable=True))
    level = db.Column(db.Integer, comment='职位级别')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    department = db.relationship('Department', backref='positions', lazy=True)

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'department_id': self.department_id,
                'department_name': self.department.name if self.department else None,
                'level': self.level,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
            }
        except Exception as e:
            print(f"转换职位数据错误: position_id={self.id}, error={str(e)}")
            return None
