from app import create_app, db
from sqlalchemy import text

def clean_db():
    """清理数据库"""
    app = create_app()
    with app.app_context():
        # 使用事务上下文管理器
        with db.engine.begin() as connection:
            try:
                # 禁用外键检查
                connection.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
                
                # 获取所有表名
                result = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'personnel_management';"
                ))
                tables = [row[0] for row in result]
                
                # 删除所有表
                for table in tables:
                    connection.execute(text(f'DROP TABLE IF EXISTS {table};'))
                
                # 启用外键检查
                connection.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))
                
                print("数据库表已清理完成")
                
            except Exception as e:
                print(f"清理数据库时出错: {str(e)}")
                raise  # 让事务自动回滚

if __name__ == '__main__':
    clean_db()
