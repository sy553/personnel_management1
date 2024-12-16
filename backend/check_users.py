from app import create_app, db
from app.models import User

def check_users():
    app = create_app()
    with app.app_context():
        # 查询用户
        users = User.query.filter(User.username.in_(['zhangsan', 'lisi'])).all()
        
        print("\n=== 用户查询结果 ===")
        if not users:
            print("未找到测试用户！")
        
        for user in users:
            print(f"\n用户名: {user.username}")
            print(f"邮箱: {user.email}")
            print(f"角色: {user.role}")
            print(f"是否激活: {user.is_active}")
            print("-" * 20)

if __name__ == '__main__':
    check_users()
