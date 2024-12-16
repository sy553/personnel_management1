from app import create_app, db
from app.models.employee import Employee

def update_photo_urls():
    app = create_app()
    with app.app_context():
        employees = Employee.query.all()
        for emp in employees:
            if emp.photo_url:
                # 提取文件名
                filename = emp.photo_url.split('/')[-1]
                # 更新为新的URL格式
                emp.photo_url = f'/photos/{filename}'
        db.session.commit()
        print("Photo URLs updated successfully")

if __name__ == '__main__':
    update_photo_urls()
