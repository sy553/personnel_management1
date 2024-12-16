"""
实习和转正状态管理模型
"""

from app import db
from datetime import datetime
from sqlalchemy import ForeignKey

class InternStatus(db.Model):
    """实习状态表 - 用于跟踪员工的实习和转正状态"""
    __tablename__ = 'intern_status'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, ForeignKey('employees.id', name='fk_intern_employee'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='intern')  # intern-实习中, probation-试用期, regular-正式
    start_date = db.Column(db.Date, nullable=False)  # 状态开始日期
    planned_end_date = db.Column(db.Date)  # 计划结束日期
    actual_end_date = db.Column(db.Date)  # 实际结束日期
    mentor_id = db.Column(db.Integer, ForeignKey('employees.id', name='fk_intern_mentor'))  # 导师ID
    department_id = db.Column(db.Integer, ForeignKey('departments.id', name='fk_intern_department'))  # 实习部门
    position_id = db.Column(db.Integer, ForeignKey('positions.id', name='fk_intern_position'))  # 实习职位
    comments = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref=db.backref('intern_status', lazy='dynamic'))
    mentor = db.relationship('Employee', foreign_keys=[mentor_id], backref=db.backref('mentoring', lazy='dynamic'))
    department = db.relationship('Department')
    position = db.relationship('Position')
    evaluations = db.relationship('InternEvaluation', back_populates='intern_status', lazy='dynamic')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'status': self.status,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'planned_end_date': self.planned_end_date.strftime('%Y-%m-%d') if self.planned_end_date else None,
            'actual_end_date': self.actual_end_date.strftime('%Y-%m-%d') if self.actual_end_date else None,
            'mentor_id': self.mentor_id,
            'mentor_name': self.mentor.name if self.mentor else None,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'position_id': self.position_id,
            'position_name': self.position.name if self.position else None,
            'comments': self.comments,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InternEvaluation(db.Model):
    """实习评估表 - 用于记录实习评估结果"""
    __tablename__ = 'intern_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    intern_status_id = db.Column(db.Integer, ForeignKey('intern_status.id', name='fk_evaluation_status'), nullable=False)
    evaluation_date = db.Column(db.Date, nullable=False)  # 评估日期
    evaluation_type = db.Column(db.String(20), nullable=False)  # monthly-月度评估, final-转正评估
    
    # 评分项（1-5分）
    work_performance = db.Column(db.Integer, nullable=False)  # 工作表现
    learning_ability = db.Column(db.Integer, nullable=False)  # 学习能力
    communication_skill = db.Column(db.Integer, nullable=False)  # 沟通能力
    professional_skill = db.Column(db.Integer, nullable=False)  # 专业技能
    attendance = db.Column(db.Integer, nullable=False)  # 出勤情况
    total_score = db.Column(db.Integer, nullable=False)  # 总分
    
    evaluation_content = db.Column(db.Text)  # 评价内容
    improvement_suggestions = db.Column(db.Text)  # 改进建议
    
    # 转正相关
    conversion_recommended = db.Column(db.Boolean, default=False)  # 是否推荐转正
    recommended_position_id = db.Column(db.Integer, ForeignKey('positions.id', name='fk_evaluation_position'))  # 建议转正职位
    recommended_salary = db.Column(db.Numeric(10, 2))  # 建议转正工资
    conversion_comments = db.Column(db.Text)  # 转正意见
    
    evaluator_id = db.Column(db.Integer, ForeignKey('employees.id', name='fk_evaluation_evaluator'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    intern_status = db.relationship('InternStatus', back_populates='evaluations')
    recommended_position = db.relationship('Position')
    evaluator = db.relationship('Employee')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'intern_status_id': self.intern_status_id,
            'evaluation_date': self.evaluation_date.strftime('%Y-%m-%d') if self.evaluation_date else None,
            'evaluation_type': self.evaluation_type,
            'work_performance': self.work_performance,
            'learning_ability': self.learning_ability,
            'communication_skill': self.communication_skill,
            'professional_skill': self.professional_skill,
            'attendance': self.attendance,
            'total_score': self.total_score,
            'evaluation_content': self.evaluation_content,
            'improvement_suggestions': self.improvement_suggestions,
            'conversion_recommended': self.conversion_recommended,
            'recommended_position_id': self.recommended_position_id,
            'recommended_position_name': self.recommended_position.name if self.recommended_position else None,
            'recommended_salary': float(self.recommended_salary) if self.recommended_salary else None,
            'conversion_comments': self.conversion_comments,
            'evaluator_id': self.evaluator_id,
            'evaluator_name': self.evaluator.name if self.evaluator else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
