import importlib
from app import create_app, db

def reset_database():
    # 重新加载应用和模型
    import app
    import app.models
    importlib.reload(app)
    importlib.reload(app.models)
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 删除所有表
        db.drop_all()
        # 创建所有表
        db.create_all()
        print("数据库已重置")

if __name__ == '__main__':
    reset_database()
