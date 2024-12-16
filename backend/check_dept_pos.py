from app import create_app, db
from app.models import Department, Position
from sqlalchemy import text
from sqlalchemy.orm import joinedload

def check_departments_and_positions():
    """检查部门和职位数据"""
    try:
        app = create_app()
        with app.app_context():
            # 显示部门数据
            print("\n=== departments表中的所有数据 ===\n")
            departments = Department.query.all()
            for dept in departments:
                print(f"部门ID: {dept.id}")
                print(f"部门名称: {dept.name}")
                print(f"部门描述: {dept.description}")
                print(f"部门主管: {'未指定' if not dept.manager_id else dept.manager_id}")
                print(f"创建时间: {dept.created_at}")
                print("-" * 20 + "\n")

            # 显示职位表结构和数据
            print("=== positions表中的所有数据 ===\n")
            # 获取表结构
            result = db.session.execute(text("""
                DESCRIBE positions;
            """))
            print("职位表结构：")
            for row in result.fetchall():
                print(f"字段名: {row[0]}, 类型: {row[1]}, 是否可空: {row[2]}, 键类型: {row[3]}, 默认值: {row[4]}")
            print("-" * 20)

            # 查询职位数据
            result = db.session.execute(text("""
                SELECT p.*, d.name as department_name 
                FROM positions p 
                LEFT JOIN departments d ON p.department_id = d.id
            """))
            
            rows = result.fetchall()
            if not rows:
                print("没有找到职位数据")
                return

            for row in rows:
                print(f"\n职位ID: {row.id}")
                print(f"职位名称: {row.name}")
                print(f"职位描述: {row.description}")
                print(f"所属部门: {row.department_name}")
                print(f"职位级别: {row.level}")
                print(f"创建时间: {row.created_at}")
                print("-" * 20)

    except Exception as e:
        print(f"查询数据时出错: {str(e)}")
        raise e

if __name__ == '__main__':
    check_departments_and_positions()
