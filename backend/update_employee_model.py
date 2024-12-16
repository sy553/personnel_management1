from app import create_app, db
from sqlalchemy import text

def update_employee_model():
    """更新员工模型，修改user_id为可空"""
    try:
        app = create_app()
        with app.app_context():
            with db.engine.begin() as conn:
                # 修改user_id字段为可空
                conn.execute(text("""
                    ALTER TABLE employees 
                    MODIFY COLUMN user_id INT NULL;
                """))
                
                print("成功更新员工表结构")
    except Exception as e:
        print(f"更新表结构时出错: {str(e)}")
        raise e

if __name__ == '__main__':
    update_employee_model()
