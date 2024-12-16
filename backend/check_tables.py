from app import create_app, db
from app.models.department import Department
from app.models.position import Position
from app.models.employee import Employee
from app.models.user import User

app = create_app('development')

with app.app_context():
    try:
        # 检查数据库连接
        db.engine.connect()
        print("\n=== 数据库连接状态 ===")
        print("数据库连接成功！")
        
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print("\n=== 现有数据表 ===")
        print("数据表列表:", existing_tables)
        
        # 检查各表数据
        print("\n=== 部门表 ===")
        dept_count = Department.query.count()
        print(f"部门总数: {dept_count}")
        if dept_count > 0:
            depts = Department.query.all()
            for dept in depts:
                print(f"- {dept.name}")

        print("\n=== 职位表 ===")
        pos_count = Position.query.count()
        print(f"职位总数: {pos_count}")
        if pos_count > 0:
            positions = Position.query.all()
            for pos in positions:
                print(f"- {pos.name}")

        print("\n=== 员工表 ===")
        emp_count = Employee.query.count()
        print(f"员工总数: {emp_count}")
        if emp_count > 0:
            employees = Employee.query.limit(5).all()
            print("最近5名员工:")
            for emp in employees:
                print(f"- {emp.name} ({emp.department.name if emp.department else '无部门'})")
                
        print("\n=== 用户表 ===")
        user_count = User.query.count()
        print(f"用户总数: {user_count}")
        if user_count > 0:
            users = User.query.all()
            for user in users:
                print(f"- {user.username} ({'管理员' if user.is_admin else '普通用户'})")
                
    except Exception as e:
        print("错误：", str(e))
