from app import create_app, db
from sqlalchemy import text
from app.models import SalaryStructure, SalaryStructureAssignment

def check_database():
    """检查数据库中的工资结构和工资结构分配"""
    app = create_app()
    with app.app_context():
        # 确保连接到正确的数据库
        db.session.execute(text("USE personnel_management"))
        
        # 直接执行SQL查询
        result = db.session.execute(text("SELECT * FROM users"))
        rows = result.fetchall()
        
        print("\n=== users表中的所有数据 ===")
        if not rows:
            print("users表中没有数据！")
        else:
            for row in rows:
                print(f"\nID: {row.id}")
                print(f"用户名: {row.username}")
                print(f"邮箱: {row.email}")
                print(f"角色: {row.role}")
                print(f"是否激活: {row.is_active}")
                print("-" * 20)

        # 检查工资结构
        print("\n=== 工资结构表中的所有数据 ===")
        salary_structures = SalaryStructure.query.all()
        if not salary_structures:
            print("工资结构表中没有数据！")
        else:
            for structure in salary_structures:
                print(f"\nID: {structure.id}")
                print(f"名称: {structure.name}")
                print(f"基本工资: {structure.basic_salary}")
                print(f"住房补贴: {structure.housing_allowance}")
                print(f"交通补贴: {structure.transport_allowance}")
                print(f"餐饮补贴: {structure.meal_allowance}")
                print(f"是否默认: {structure.is_default}")
                print(f"是否激活: {structure.is_active}")
                print("-" * 20)

        # 检查工资结构分配
        print("\n=== 工资结构分配表中的所有数据 ===")
        assignments = SalaryStructureAssignment.query.all()
        if not assignments:
            print("工资结构分配表中没有数据！")
        else:
            for assignment in assignments:
                print(f"\nID: {assignment.id}")
                print(f"工资结构ID: {assignment.salary_structure_id}")
                print(f"部门ID: {assignment.department_id}")
                print(f"员工ID: {assignment.employee_id}")
                print(f"是否默认: {assignment.is_default}")
                print(f"是否激活: {assignment.is_active}")
                print(f"生效日期: {assignment.effective_date}")
                print("-" * 20)

        # 检查数据库连接信息
        result = db.session.execute(text("SELECT DATABASE()"))
        current_db = result.scalar()
        print(f"\n当前连接的数据库: {current_db}")

if __name__ == '__main__':
    check_database()
