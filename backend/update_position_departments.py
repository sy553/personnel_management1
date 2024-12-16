from app import create_app, db
from sqlalchemy import text

def update_position_departments():
    """更新职位的部门关联"""
    try:
        app = create_app()
        with app.app_context():
            with db.engine.begin() as conn:
                # 更新技术部职位
                conn.execute(text("""
                    UPDATE positions 
                    SET department_id = 1 
                    WHERE id IN (1, 2);
                """))
                
                # 更新人事部职位
                conn.execute(text("""
                    UPDATE positions 
                    SET department_id = 2 
                    WHERE id = 3;
                """))
                
                # 更新财务部职位
                conn.execute(text("""
                    UPDATE positions 
                    SET department_id = 3 
                    WHERE id = 4;
                """))
                
                print("成功更新职位的部门关联")
    except Exception as e:
        print(f"更新部门关联时出错: {str(e)}")
        raise e

if __name__ == '__main__':
    update_position_departments()
