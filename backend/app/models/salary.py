from app import db
from datetime import datetime

class SalaryStructure(db.Model):
    """薪资结构表 - 用于定义不同职位或级别的薪资模板"""
    __tablename__ = 'salary_structures'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, comment='薪资结构名称')
    description = db.Column(db.String(200), comment='描述')
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False, comment='基本工资')
    housing_allowance = db.Column(db.Numeric(10, 2), default=0, comment='住房补贴')
    transport_allowance = db.Column(db.Numeric(10, 2), default=0, comment='交通补贴')
    meal_allowance = db.Column(db.Numeric(10, 2), default=0, comment='餐饮补贴')
    effective_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date(), comment='生效日期')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认薪资结构')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), comment='员工ID，如果为空则为通用薪资结构')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    employee = db.relationship('Employee', backref=db.backref('salary_structures', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'basic_salary': float(self.basic_salary),
            'housing_allowance': float(self.housing_allowance),
            'transport_allowance': float(self.transport_allowance),
            'meal_allowance': float(self.meal_allowance),
            'effective_date': self.effective_date.strftime('%Y-%m-%d'),
            'is_default': self.is_default,
            'is_active': self.is_active,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class SalaryRecord(db.Model):
    """薪资发放记录表"""
    __tablename__ = 'salary_records'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, comment='员工ID')
    year = db.Column(db.Integer, nullable=False, comment='年份')
    month = db.Column(db.Integer, nullable=False, comment='月份')
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False, comment='基本工资')
    allowances = db.Column(db.Numeric(10, 2), default=0, comment='补贴总额')
    overtime_pay = db.Column(db.Numeric(10, 2), default=0, comment='加班费')
    bonus = db.Column(db.Numeric(10, 2), default=0, comment='奖金')
    deductions = db.Column(db.Numeric(10, 2), default=0, comment='扣除项(请假等)')
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False, comment='应发总额')
    tax = db.Column(db.Numeric(10, 2), default=0, comment='个人所得税')
    net_salary = db.Column(db.Numeric(10, 2), nullable=False, comment='实发工资')
    payment_status = db.Column(db.String(20), default='pending', comment='发放状态(pending/paid)')
    payment_date = db.Column(db.DateTime, comment='发放日期')
    remark = db.Column(db.String(1000), comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    employee = db.relationship('Employee', backref=db.backref('salary_records', lazy='dynamic'))

    def to_dict(self):
        """
        转换工资记录为字典格式
        
        返回:
            dict: 包含以下字段的字典:
                - id: 工资记录ID
                - employee_id: 员工ID
                - employee_name: 员工姓名
                - department_name: 部门名称
                - year: 年份
                - month: 月份
                - basic_salary: 基本工资
                - allowances: 补贴
                - overtime_pay: 加班费
                - bonus: 奖金
                - deductions: 扣除
                - gross_salary: 应发总额
                - tax: 个人所得税
                - net_salary: 实发工资
                - payment_status: 发放状态
                - payment_date: 发放日期
                - remark: 备注
                - created_at: 创建时间
                - updated_at: 更新时间
        """
        # 获取员工信息
        employee_info = {
            'name': self.employee.name if self.employee else None,
            'department': self.employee.department.name if self.employee and self.employee.department else None,
            'position': self.employee.position.name if self.employee and self.employee.position else None
        }
        
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': employee_info['name'],  # 直接提供员工姓名
            'department_name': employee_info['department'],  # 直接提供部门名称
            'position_name': employee_info['position'],  # 直接提供职位名称
            'employee': employee_info,  # 同时保留完整的员工信息对象
            'year': self.year,
            'month': self.month,
            'basic_salary': float(self.basic_salary),
            'allowances': float(self.allowances),
            'overtime_pay': float(self.overtime_pay),
            'bonus': float(self.bonus),
            'deductions': float(self.deductions),
            'gross_salary': float(self.gross_salary),
            'tax': float(self.tax),
            'net_salary': float(self.net_salary),
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.strftime('%Y-%m-%d %H:%M:%S') if self.payment_date else None,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
