from app import create_app, db
from app.models import Employee, Position
from sqlalchemy import text

def check_employees():
    app = create_app()
    with app.app_context():
        try:
            # 使用原生SQL查询employees表
            result = db.session.execute(text("""
                SELECT e.*, p.name as position_name 
                FROM employees e 
                LEFT JOIN positions p ON e.position_id = p.id
            """))
            
            rows = result.fetchall()
            
            print("\n=== employees表中的所有数据 ===")
            if not rows:
                print("employees表中没有数据！")
                return
                
            for row in rows:
                print(f"员工ID: {row.id}")
                print(f"员工编号: {row.employee_id}")
                print(f"姓名: {row.name}")
                print(f"职位: {row.position_name}")
                print(f"在职状态: {row.employment_status}")
                print("-" * 20)

        except Exception as e:
            print(f"查询数据时出错: {str(e)}")
            raise e

def check_position_employees(position_id):
    """检查指定职位ID的所有员工（包括离职员工）"""
    try:
        app = create_app()
        with app.app_context():
            # 使用原生SQL查询
            result = db.session.execute(text("""
                SELECT e.*, p.name as position_name 
                FROM employees e 
                LEFT JOIN positions p ON e.position_id = p.id 
                WHERE e.position_id = :position_id
            """), {"position_id": position_id})
            
            rows = result.fetchall()
            
            print(f"\n=== 职位ID {position_id} 的所有员工 ===\n")
            if not rows:
                print("没有找到任何员工")
                return
                
            position = Position.query.get(position_id)
            print(f"职位名称: {position.name if position else '未知'}\n")
            
            for row in rows:
                print(f"员工ID: {row.id}")
                print(f"员工编号: {row.employee_id}")
                print(f"姓名: {row.name}")
                print(f"在职状态: {row.employment_status}")
                print("-" * 20)

    except Exception as e:
        print(f"查询数据时出错: {str(e)}")
        raise e

def check_positions():
    """检查所有职位"""
    app = create_app()
    with app.app_context():
        try:
            result = db.session.execute(text("SELECT * FROM positions"))
            rows = result.fetchall()
            
            print("\n=== positions表中的所有数据 ===")
            if not rows:
                print("positions表中没有数据！")
                return
                
            for row in rows:
                print(f"职位ID: {row.id}")
                print(f"职位名称: {row.name}")
                print("-" * 20)

        except Exception as e:
            print(f"查询数据时出错: {str(e)}")
            raise e

if __name__ == '__main__':
    check_employees()
    check_positions()  # 先检查所有职位
    check_position_employees(5)  # 检查职位ID为5（行政人员）的员工
