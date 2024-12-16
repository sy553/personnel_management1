from app import create_app, db
from sqlalchemy import text

def add_department_id():
    """添加 department_id 字段到 positions 表"""
    try:
        app = create_app()
        with app.app_context():
            # 添加 department_id 字段
            with db.engine.begin() as conn:
                # 检查外键约束是否存在
                result = conn.execute(text("""
                    SELECT CONSTRAINT_NAME 
                    FROM information_schema.TABLE_CONSTRAINTS 
                    WHERE TABLE_NAME = 'positions' 
                    AND CONSTRAINT_TYPE = 'FOREIGN KEY' 
                    AND CONSTRAINT_NAME = 'fk_position_department';
                """))
                
                if result.fetchone():
                    # 如果外键存在，删除它
                    conn.execute(text("""
                        ALTER TABLE positions 
                        DROP FOREIGN KEY fk_position_department;
                    """))
                
                # 检查字段是否存在
                result = conn.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_NAME = 'positions' 
                    AND COLUMN_NAME = 'department_id';
                """))
                
                if not result.fetchone():
                    # 如果字段不存在，添加它
                    conn.execute(text("""
                        ALTER TABLE positions 
                        ADD COLUMN department_id INT;
                    """))
                
                # 添加外键约束
                conn.execute(text("""
                    ALTER TABLE positions 
                    ADD CONSTRAINT fk_position_department 
                    FOREIGN KEY (department_id) 
                    REFERENCES departments(id);
                """))
                
                print("成功添加 department_id 字段到 positions 表")
    except Exception as e:
        print(f"添加字段时出错: {str(e)}")
        raise e

if __name__ == '__main__':
    add_department_id()
