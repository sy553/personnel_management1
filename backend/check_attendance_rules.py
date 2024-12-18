from app import create_app, db
from app.models.attendance import AttendanceRule

app = create_app('development')

with app.app_context():
    # 查询所有考勤规则
    rules = AttendanceRule.query.all()
    print("\n=== 考勤规则列表 ===")
    for rule in rules:
        print(f"\n规则ID: {rule.id}")
        print(f"名称: {rule.name}")
        print(f"是否默认: {rule.is_default}")
        print(f"上班时间: {rule.work_start_time}")
        print(f"下班时间: {rule.work_end_time}")
        print(f"生效开始日期: {rule.effective_start_date}")
        print(f"生效结束日期: {rule.effective_end_date}")
        print(f"弹性工作时间: {rule.flexible_time}分钟")
        print(f"加班费率: {rule.overtime_rate}")
        print(f"周末加班费率: {rule.weekend_overtime_rate}")
        print(f"节假日加班费率: {rule.holiday_overtime_rate}")
        print(f"部门ID: {rule.department_id}")
        print("-" * 50)
