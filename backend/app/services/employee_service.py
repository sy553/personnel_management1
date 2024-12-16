from app import db
from app.models import Employee, Department, Position, User
from datetime import datetime
from sqlalchemy import or_

class EmployeeService:
    @staticmethod
    def create_employee(data):
        """
        创建新员工
        :param data: 员工信息字典
        :return: 员工对象或None
        """
        try:
            # 如果提供了 user_id，检查用户是否存在
            if data.get('user_id'):
                user = User.query.get(data['user_id'])
                if not user:
                    return None, f"用户ID {data['user_id']} 不存在"

            # 检查员工号是否已存在
            existing_employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
            if existing_employee:
                return None, f"员工号 {data['employee_id']} 已存在"
            
            # 创建员工基本信息
            employee = Employee()
            
            # 设置必填字段
            employee.user_id = data.get('user_id')  # 允许为空
            employee.employee_id = data['employee_id']
            employee.name = data['name']
            
            # 设置可选字段
            if 'gender' in data:
                employee.gender = data['gender']
            if 'birth_date' in data and data['birth_date']:
                if isinstance(data['birth_date'], str):
                    employee.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                else:
                    employee.birth_date = data['birth_date']
            if 'id_card' in data:
                employee.id_card = data['id_card']
            if 'phone' in data:
                employee.phone = data['phone']
            if 'email' in data:
                employee.email = data['email']
            if 'address' in data:
                employee.address = data['address']
            if 'department_id' in data:
                employee.department_id = data['department_id']
            if 'position_id' in data:
                employee.position_id = data['position_id']
            if 'hire_date' in data and data['hire_date']:
                if isinstance(data['hire_date'], str):
                    employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
                else:
                    employee.hire_date = data['hire_date']
            if 'employment_status' in data:
                if data['employment_status'] in ['active', 'resigned', 'suspended']:
                    employee.employment_status = data['employment_status']
                else:
                    return None, f"无效的雇佣状态: {data['employment_status']}"
            else:
                employee.employment_status = 'active'
            # 添加employee_type字段的处理
            if 'employee_type' in data:
                if data['employee_type'] in ['intern', 'probation', 'regular']:
                    employee.employee_type = data['employee_type']
                else:
                    return None, f"无效的员工类型: {data['employee_type']}"
            else:
                employee.employee_type = 'regular'  # 默认为正式员工

            db.session.add(employee)
            db.session.commit()
            return employee, None
        except Exception as e:
            db.session.rollback()
            print(f"创建员工错误: {str(e)}")
            return None, str(e)

    @staticmethod
    def update_employee(employee_id, data):
        """
        更新员工信息
        :param employee_id: 员工ID
        :param data: 更新的信息字典
        :return: 更新后的员工对象或None
        """
        try:
            # 使用 with 语句确保事务的完整性
            with db.session.begin_nested():
                employee = Employee.query.options(
                    db.joinedload(Employee.department),
                    db.joinedload(Employee.position)
                ).get(employee_id)
                
                if not employee:
                    return None, "员工不存在"

                # 更新可修改的字段
                update_fields = [
                    'name', 'gender', 'birth_date', 'id_card', 'phone', 
                    'email', 'address', 'department_id', 'position_id', 
                    'employment_status', 'hire_date', 'employee_type'
                ]
                
                # 记录更新前的状态
                old_employee_type = employee.employee_type
                old_position_id = employee.position_id
                
                for field in update_fields:
                    if field in data:
                        if field in ['birth_date', 'hire_date'] and data[field]:  
                            setattr(employee, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                        elif field == 'employment_status':
                            # 确保状态字段是有效值
                            if data[field] in ['active', 'resigned', 'suspended']:
                                setattr(employee, field, data[field])
                            else:
                                return None, f"无效的雇佣状态: {data[field]}"
                        elif field == 'employee_type':  # 添加employee_type的处理
                            # 确保employee_type字段是有效值
                            if data[field] in ['intern', 'probation', 'regular']:
                                # 检查状态转换是否合法
                                if not EmployeeService._is_valid_status_transition(old_employee_type, data[field]):
                                    return None, f"无效的员工类型转换: 从 {old_employee_type} 到 {data[field]}"
                                setattr(employee, field, data[field])
                            else:
                                return None, f"无效的员工类型: {data[field]}"        
                        else:
                            setattr(employee, field, data[field])
                
                employee.updated_at = datetime.utcnow()
                
                # 提交更改
                db.session.flush()
                
                # 返回更新后的员工对象
                return employee, None
                
        except Exception as e:
            print(f"更新员工错误: {str(e)}")
            raise  # 向上层抛出异常，由调用方处理回滚
            
    @staticmethod
    def _is_valid_status_transition(old_status, new_status):
        """
        检查状态转换是否合法
        :param old_status: 原状态
        :param new_status: 新状态
        :return: 是否合法
        """
        # 定义合法的状态转换
        valid_transitions = {
            'intern': ['probation'],  # 实习生只能转为试用期
            'probation': ['regular'],  # 试用期只能转为正式
            'regular': []  # 正式员工不能改变状态
        }
        
        # 如果是相同状态，允许
        if old_status == new_status:
            return True
            
        # 检查转换是否在允许的范围内
        return new_status in valid_transitions.get(old_status, [])

    @staticmethod
    def delete_employee(employee_id):
        """
        删除员工（软删除，将状态改为已离职）
        :param employee_id: 员工ID
        :return: 是否成功
        """
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "员工不存在"
            
            employee.employment_status = 'resigned'
            employee.updated_at = datetime.utcnow()
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"删除员工错误: {str(e)}")
            return False, str(e)

    @staticmethod
    def get_employee(employee_id):
        """
        获取单个员工信息
        :param employee_id: 员工ID
        :return: (员工对象, 错误信息)
        """
        try:
            employee = Employee.query.options(
                db.joinedload(Employee.department),
                db.joinedload(Employee.position),
                db.joinedload(Employee.user)  # 确保加载user关系
            ).get(employee_id)
            
            if not employee:
                return None, "员工不存在"
                
            return employee, None
        except Exception as e:
            print(f"获取员工错误: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_employees(page=1, per_page=10, search=None, department_id=None, position_id=None, gender=None, education=None):
        """
        获取员工列表
        :param page: 页码
        :param per_page: 每页数量
        :param search: 搜索关键词
        :param department_id: 部门ID筛选
        :param position_id: 职位ID筛选
        :param gender: 性别筛选
        :param education: 学历筛选
        :return: (员工列表, 总数, 错误信息)
        """
        try:
            # 构建基础查询
            query = Employee.query.filter(Employee.employment_status != 'resigned').options(
                db.joinedload(Employee.department),
                db.joinedload(Employee.position),
                db.joinedload(Employee.user)
            )
            
            # 添加搜索条件
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Employee.name.ilike(search_term),
                        Employee.employee_id.ilike(search_term),
                        Employee.phone.ilike(search_term),
                        Employee.email.ilike(search_term)
                    )
                )
                
            # 添加部门筛选
            if department_id:
                query = query.filter(Employee.department_id == department_id)
                
            # 添加职位筛选
            if position_id:
                query = query.filter(Employee.position_id == position_id)
                
            # 添加性别筛选
            if gender:
                query = query.filter(Employee.gender == gender)
                
            # 添加学历筛选
            if education:
                query = query.filter(Employee.education == education)
                
            # 获取总数
            total = query.count()
            
            # 分页
            employees = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return employees, total, None
            
        except Exception as e:
            print(f"获取员工列表错误: {str(e)}")
            return [], 0, str(e)

class DepartmentService:
    @staticmethod
    def create_department(data):
        """
        创建新部门
        :param data: 部门信息字典
        :return: 部门对象或None
        """
        try:
            department = Department(
                name=data['name'],
                description=data.get('description'),
                parent_id=data.get('parent_id'),
                manager_id=data.get('manager_id'),
                level=data.get('level', 1)
            )
            db.session.add(department)
            db.session.commit()
            return department, None
        except Exception as e:
            db.session.rollback()
            print(f"创建部门错误: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_departments():
        """
        获取所有部门列表
        :return: (部门列表, 错误信息)
        """
        try:
            print("开始获取部门列表...")
            departments = Department.query.all()
            print(f"查询到 {len(departments)} 个部门")
            
            # 处理每个部门的数据
            department_list = []
            for dept in departments:
                dept_dict = dept.to_dict()
                department_list.append(dept_dict)
            
            print("成功处理 {} 个部门的数据".format(len(department_list)))
            return department_list, None
        except Exception as e:
            print(f"获取部门列表错误: {str(e)}")
            return [], str(e)

    @staticmethod
    def delete_department(department_id):
        """
        删除部门
        :param department_id: 部门ID
        :return: (成功标志, 错误信息)
        """
        try:
            department = Department.query.get(department_id)
            if not department:
                return False, "部门不存在"
            
            # 检查是否有员工属于该部门
            if department.employees.count() > 0:
                return False, "该部门下还有员工，无法删除"
                
            db.session.delete(department)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"删除部门错误: {str(e)}")
            return False, str(e)

    @staticmethod
    def update_department(department_id, data):
        """
        更新部门信息
        :param department_id: 部门ID
        :param data: 更新的信息字典
        :return: (更新后的部门对象, 错误信息)
        """
        try:
            department = Department.query.get(department_id)
            if not department:
                return None, "部门不存在"
            
            # 更新字段
            if 'name' in data:
                department.name = data['name']
            if 'description' in data:
                department.description = data['description']
            if 'parent_id' in data:
                department.parent_id = data['parent_id']
            if 'manager_id' in data:
                department.manager_id = data['manager_id']
            if 'level' in data:
                department.level = data['level']
                
            department.updated_at = datetime.utcnow()
            db.session.commit()
            return department, None
        except Exception as e:
            db.session.rollback()
            print(f"更新部门错误: {str(e)}")
            return None, str(e)

class PositionService:
    @staticmethod
    def create_position(data):
        """
        创建新职位
        :param data: 职位信息字典
        :return: (职位对象, 错误信息)
        """
        try:
            position = Position(
                name=data['name'],
                description=data.get('description'),
                level=data.get('level', 1)
            )
            db.session.add(position)
            db.session.commit()
            return position, None
        except Exception as e:
            db.session.rollback()
            print(f"创建职位错误: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_positions():
        """
        获取所有职位列表
        :return: (职位列表, 错误信息)
        """
        try:
            positions = Position.query.all()
            position_list = []
            for pos in positions:
                position_list.append(pos.to_dict())
            print(f"成功获取到 {len(position_list)} 个职位")
            return position_list, None
        except Exception as e:
            print(f"获取职位列表错误: {str(e)}")
            return [], str(e)

    @staticmethod
    def update_position(position_id, data):
        """
        更新职位信息
        :param position_id: 职位ID
        :param data: 更新的信息字典
        :return: (更新后的职位对象, 错误信息)
        """
        try:
            position = Position.query.get(position_id)
            if not position:
                return None, "职位不存在"
            
            # 更新字段
            if 'name' in data:
                position.name = data['name']
            if 'description' in data:
                position.description = data['description']
            if 'level' in data:
                position.level = data['level']
                
            position.updated_at = datetime.utcnow()
            db.session.commit()
            return position, None
        except Exception as e:
            db.session.rollback()
            print(f"更新职位错误: {str(e)}")
            return None, str(e)

    @staticmethod
    def delete_position(position_id):
        """
        删除职位
        :param position_id: 职位ID
        :return: (成功标志, 错误信息)
        """
        try:
            position = Position.query.get(position_id)
            if not position:
                return False, "职位不存在"
            
            # 检查是否有员工属于该职位
            if position.employees.count() > 0:
                return False, "该职位下还有员工，无法删除"
                
            db.session.delete(position)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"删除职位错误: {str(e)}")
            return False, str(e)
