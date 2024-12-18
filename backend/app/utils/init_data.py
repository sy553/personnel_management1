"""
初始化数据工具模块
用于初始化系统必要的基础数据
"""
from app import db
from app.models.attendance import AttendanceRule
from datetime import time, datetime

def init_default_attendance_rule():
    """
    初始化默认考勤规则
    如果不存在默认规则，则创建一个默认的考勤规则
    """
    try:
        # 检查是否已存在默认规则（只查询必要字段）
        default_rule = db.session.query(
            AttendanceRule.id,
            AttendanceRule.name,
            AttendanceRule.is_default
        ).filter_by(is_default=True).first()
        
        if not default_rule:
            # 创建默认考勤规则
            default_rule = AttendanceRule(
                name='标准工作制',
                work_start_time=time(9, 0),  # 上班时间 9:00
                work_end_time=time(18, 0),   # 下班时间 18:00
                late_threshold=15,           # 迟到阈值15分钟
                early_leave_threshold=15,    # 早退阈值15分钟
                overtime_minimum=60,         # 最小加班时长1小时
                is_default=True,
                description='标准工作制：朝九晚六，午休1小时',
                effective_start_date=datetime.now().date()  # 设置生效开始日期为当前日期
            )
            db.session.add(default_rule)
            db.session.commit()
            print('成功创建默认考勤规则')
        return True
    except Exception as e:
        print(f'初始化默认考勤规则失败: {str(e)}')
        db.session.rollback()
        return False

def init_attendance_rules():
    """初始化考勤规则数据"""
    rules_data = [
        {
            'name': '标准工作制',
            'description': '朝九晚五，每周五天',
            'work_start_time': '09:00:00',
            'work_end_time': '17:00:00',
            'break_start_time': '12:00:00',
            'break_end_time': '13:00:00',
            'workdays': '1,2,3,4,5',  # 周一到周五
            'priority': 1,
            'status': 1
        },
        {
            'name': '弹性工作制',
            'description': '弹性工作时间，核心工作时间10:00-16:00',
            'work_start_time': '08:00:00',
            'work_end_time': '18:00:00',
            'break_start_time': '12:00:00',
            'break_end_time': '13:00:00',
            'workdays': '1,2,3,4,5',  # 周一到周五
            'priority': 2,
            'status': 1
        }
    ]
    
    for rule_data in rules_data:
        rule = AttendanceRule.query.filter_by(name=rule_data['name']).first()
        if not rule:
            rule = AttendanceRule(**rule_data)
            db.session.add(rule)
    
    try:
        db.session.commit()
        print("考勤规则初始化成功")
    except Exception as e:
        db.session.rollback()
        print(f"考勤规则初始化失败: {str(e)}")
