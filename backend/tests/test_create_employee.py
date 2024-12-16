import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.employee_service import EmployeeService
from app.models import Employee

def test_create_employee():
    """测试创建员工功能"""
    app = create_app()
    
    with app.app_context():
        # 使用时间戳生成唯一的员工号
        unique_id = int(time.time())
        
        # 准备测试数据
        employee_data = {
            'employee_id': f'EMP{unique_id}',
            'name': '张三',
            'gender': '男',
            'phone': '13800138000',
            'email': 'zhangsan@example.com',
            'address': '北京市朝阳区',
            'birth_date': '1990-01-01',
            'hire_date': '2023-01-01',
            'employment_status': '在职'
        }
        
        # 测试创建员工
        employee, message = EmployeeService.create_employee(employee_data)
        
        if employee:
            print("测试成功！成功创建员工：")
            print(f"员工ID: {employee.employee_id}")
            print(f"姓名: {employee.name}")
            print(f"性别: {employee.gender}")
            print(f"邮箱: {employee.email}")
            print(f"状态: {employee.employment_status}")
            print(f"用户ID: {employee.user_id}")  # 验证 user_id 为空
            
            # 清理测试数据
            db.session.delete(employee)
            db.session.commit()
            print("测试数据已清理")
        else:
            print(f"测试失败！错误信息：{message}")

if __name__ == '__main__':
    test_create_employee()
