import os
import importlib
from app import create_app, db
import pymysql
from flask_migrate import upgrade

def reset_database():
    # 设置环境变量
    os.environ['FLASK_APP'] = 'app'
    os.environ['FLASK_ENV'] = 'development'
    
    # 重新加载应用和模型
    import app
    import app.models
    importlib.reload(app)
    importlib.reload(app.models)
    
    # 创建应用上下文
    flask_app = create_app('development')
    
    with flask_app.app_context():
        # 获取数据库连接信息
        db_name = 'personnel_management'
        db_user = 'root'
        db_pass = '123456'
        db_host = 'localhost'
        
        # 创建数据库连接
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            charset='utf8mb4'
        )
        
        try:
            with conn.cursor() as cursor:
                # 删除数据库
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                # 重新创建数据库
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"数据库 {db_name} 已重置")
            conn.commit()
        finally:
            conn.close()
        
        # 重新连接到新创建的数据库
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            db=db_name,
            charset='utf8mb4'
        )
        
        try:
            with conn.cursor() as cursor:
                # 创建 alembic_version 表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    )
                """)
            conn.commit()
        finally:
            conn.close()
        
        # 运行所有迁移
        upgrade()
        print("数据库迁移完成")

if __name__ == '__main__':
    reset_database()
