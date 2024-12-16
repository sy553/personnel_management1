import os
import sys
import logging
from datetime import date
import importlib
import pymysql
from sqlalchemy import text

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app import create_app, db
from app.models import User, Department, Position, Employee, SalaryStructure, SalaryStructureAssignment

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """创建数据库"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS personnel_management")
        connection.commit()
        logger.info("数据库创建成功或已存在")
    except Exception as e:
        logger.error(f"创建数据库时出错: {str(e)}")
        raise e
    finally:
        if connection:
            connection.close()

def drop_all_tables():
    """手动删除所有表"""
    try:
        # 禁用外键检查
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
        
        # 获取所有表名
        tables = [
            'users', 'departments', 'positions', 'employees',
            'attendances', 'leaves', 'overtimes',
            'salary_records', 'salary_structures', 'salary_structure_assignments'
        ]
        
        # 删除每个表
        for table in tables:
            try:
                db.session.execute(text(f'DROP TABLE IF EXISTS {table};'))
                print(f"表 {table} 删除成功")
            except Exception as e:
                print(f"删除表 {table} 时出错: {str(e)}")
        
        # 启用外键检查
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def clear_data():
    """清除现有数据"""
    try:
        # 使用原生SQL删除现有数据
        with db.engine.begin() as connection:
            # 禁用外键检查
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 清空所有表
            connection.execute(text("TRUNCATE TABLE employees"))
            connection.execute(text("TRUNCATE TABLE positions"))
            connection.execute(text("TRUNCATE TABLE departments"))
            connection.execute(text("TRUNCATE TABLE users"))
            connection.execute(text("TRUNCATE TABLE salary_structures"))
            connection.execute(text("TRUNCATE TABLE salary_structure_assignments"))
            
            # 启用外键检查
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    except Exception as e:
        print(f"清除数据时出错: {str(e)}")
        db.session.rollback()
        raise e

def create_users():
    """创建管理员用户"""
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)

def create_test_user():
    """创建测试用户"""
    users_data = [
        {
            'username': 'zhangsan',
            'email': 'zhangsan@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'username': 'lisi',
            'email': 'lisi@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'username': 'wangwu',
            'email': 'wangwu@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'username': 'zhaoliu',
            'email': 'zhaoliu@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'username': 'sunqi',
            'email': 'sunqi@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'username': 'zhouba',
            'email': 'zhouba@example.com',
            'password': 'password123',
            'role': 'user'
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        users.append(user)

def create_departments():
    """创建部门"""
    departments_data = [
        {'name': '技术部', 'description': '负责公司技术研发'},
        {'name': '人事部', 'description': '负责公司人事管理'},
        {'name': '财务部', 'description': '负责公司财务管理'},
        {'name': '市场部', 'description': '负责公司市场营销'}
    ]
    
    departments = []
    for dept_data in departments_data:
        dept = Department(**dept_data)
        db.session.add(dept)
        departments.append(dept)

def create_positions():
    """创建职位"""
    positions_data = [
        {
            'name': '软件工程师',
            'description': '负责软件开发',
            'department_id': 1,
            'level': 1
        },
        {
            'name': '高级工程师',
            'description': '负责技术架构',
            'department_id': 1,
            'level': 2
        },
        {
            'name': 'HR专员',
            'description': '负责招聘',
            'department_id': 2,
            'level': 1
        },
        {
            'name': '财务专员',
            'description': '负责财务核算',
            'department_id': 3,
            'level': 1
        }
    ]
    
    for pos_data in positions_data:
        position = Position()
        for key, value in pos_data.items():
            setattr(position, key, value)
        db.session.add(position)

def create_employees():
    """创建员工"""
    employees_data = [
        {
            'user_id': 1,
            'employee_id': 'EMP001',
            'name': '张三',
            'gender': '男',
            'birth_date': date(1990, 1, 1),
            'id_card': '110101199001011234',
            'phone': '13800138001',
            'address': '北京市朝阳区',
            'department_id': 1,
            'position_id': 1,
            'hire_date': date(2020, 1, 1),
            'employment_status': 'active'
        },
        {
            'user_id': 2,
            'employee_id': 'EMP002',
            'name': '李四',
            'gender': '女',
            'birth_date': date(1992, 2, 2),
            'id_card': '110101199202022345',
            'phone': '13800138002',
            'address': '北京市海淀区',
            'department_id': 2,
            'position_id': 3,
            'hire_date': date(2020, 2, 1),
            'employment_status': 'active'
        },
        {
            'user_id': 3,
            'employee_id': 'EMP003',
            'name': '王五',
            'gender': '男',
            'birth_date': date(1988, 3, 15),
            'id_card': '110101198803153456',
            'phone': '13800138003',
            'address': '北京市西城区',
            'department_id': 1,
            'position_id': 2,
            'hire_date': date(2019, 6, 1),
            'employment_status': 'active'
        },
        {
            'user_id': 4,
            'employee_id': 'EMP004',
            'name': '赵六',
            'gender': '女',
            'birth_date': date(1995, 7, 20),
            'id_card': '110101199507204567',
            'phone': '13800138004',
            'address': '北京市东城区',
            'department_id': 3,
            'position_id': 4,
            'hire_date': date(2021, 3, 1),
            'employment_status': 'active'
        },
        {
            'user_id': 5,
            'employee_id': 'EMP005',
            'name': '孙七',
            'gender': '男',
            'birth_date': date(1991, 12, 25),
            'id_card': '110101199112255678',
            'phone': '13800138005',
            'address': '北京市丰台区',
            'department_id': 1,
            'position_id': 1,
            'hire_date': date(2018, 9, 1),
            'resignation_date': date(2023, 6, 30),
            'employment_status': 'resigned'
        },
        {
            'user_id': 6,
            'employee_id': 'EMP006',
            'name': '周八',
            'gender': '女',
            'birth_date': date(1993, 8, 8),
            'id_card': '110101199308086789',
            'phone': '13800138006',
            'address': '北京市石景山区',
            'department_id': 2,
            'position_id': 3,
            'hire_date': date(2019, 4, 1),
            'resignation_date': date(2023, 8, 31),
            'employment_status': 'resigned'
        }
    ]
    
    for emp_data in employees_data:
        employee = Employee(**emp_data)
        db.session.add(employee)

def create_salary_structures():
    """创建工资结构和工资结构分配"""
    try:
        # 清除现有的工资结构和分配
        SalaryStructureAssignment.query.delete()
        SalaryStructure.query.delete()
        db.session.commit()
        
        # 创建基本工资结构
        basic_structure = SalaryStructure(
            name='基本工资结构',
            description='适用于所有员工的基本工资结构',
            basic_salary=5000,  # 基本工资
            housing_allowance=1000,  # 住房补贴
            transport_allowance=500,  # 交通补贴
            meal_allowance=500,  # 餐饮补贴
            is_default=True,  # 设置为默认工资结构
            is_active=True  # 设置为激活状态
        )
        db.session.add(basic_structure)
        db.session.flush()  # 获取ID
        
        print(f"创建基本工资结构成功，ID: {basic_structure.id}")
        
        # 创建全局默认的工资结构分配（优先级最低）
        global_assignment = SalaryStructureAssignment(
            salary_structure_id=basic_structure.id,
            is_default=True,  # 设置为全局默认
            effective_date=date(2024, 1, 1),  # 从2024年1月1日生效
            is_active=True  # 设置为激活状态
        )
        db.session.add(global_assignment)
        print("创建全局默认工资结构分配")
        
        # 为每个部门创建工资结构分配（优先级中等）
        departments = Department.query.all()
        for dept in departments:
            dept_assignment = SalaryStructureAssignment(
                salary_structure_id=basic_structure.id,
                department_id=dept.id,  # 设置部门ID
                is_default=False,  # 设置为非默认，只有全局工资结构是默认的
                effective_date=date(2024, 1, 1),  # 从2024年1月1日生效
                is_active=True  # 设置为激活状态
            )
            db.session.add(dept_assignment)
            print(f"为部门 {dept.name} 创建工资结构分配")
        
        # 为特定员工创建工资结构分配（优先级最高）
        employees = Employee.query.filter(Employee.id.in_([1, 3, 5])).all()  # 只为部分员工创建专属工资结构
        for emp in employees:
            emp_assignment = SalaryStructureAssignment(
                salary_structure_id=basic_structure.id,
                employee_id=emp.id,  # 设置员工ID
                is_default=False,  # 设置为非默认
                effective_date=date(2024, 1, 1),  # 从2024年1月1日生效
                is_active=True  # 设置为激活状态
            )
            db.session.add(emp_assignment)
            print(f"为员工 {emp.name} 创建工资结构分配")
        
        # 提交事务
        db.session.commit()
        print("工资结构和分配初始化成功")
        
    except Exception as e:
        print(f"初始化工资结构时出错: {str(e)}")
        db.session.rollback()
        raise e

def init_db():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        try:
            # 创建数据库（如果不存在）
            create_database()
            
            # 删除所有表（如果存在）
            drop_all_tables()
            
            # 创建所有表
            db.create_all()
            print("数据库表创建成功")
            
            # 清除现有数据
            clear_data()
            print("现有数据清除成功")
            
            # 创建管理员用户
            create_users()
            print("管理员用户创建成功")
            
            # 创建测试用户
            create_test_user()
            print("测试用户创建成功")
            
            # 创建部门
            create_departments()
            print("部门创建成功")
            
            # 创建职位
            create_positions()
            print("职位创建成功")
            
            # 创建员工
            create_employees()
            print("员工创建成功")
            
            # 创建工资结构和分配
            create_salary_structures()
            print("工资结构创建成功")
            
            db.session.commit()
            print("数据库初始化完成")
            
        except Exception as e:
            print(f"初始化数据库时出错: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == '__main__':
    init_db()
