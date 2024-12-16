from app import create_app, db
from app.models import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        # 检查是否已存在管理员用户
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Admin user already exists!')
            return
        
        # 创建新的管理员用户
        user = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            is_active=True
        )
        user.set_password('admin123')
        
        try:
            db.session.add(user)
            db.session.commit()
            print('Admin user created successfully!')
        except Exception as e:
            db.session.rollback()
            print(f'Error creating admin user: {str(e)}')

if __name__ == '__main__':
    create_admin_user()
