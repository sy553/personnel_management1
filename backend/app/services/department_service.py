from app import db
from app.models import Department, Employee
from sqlalchemy import or_

class DepartmentService:
    @staticmethod
    def get_departments():
        """
        获取部门列表
        :return: 部门列表
        """
        try:
            departments = Department.query.all()
            return departments
        except Exception as e:
            print(f"获取部门列表错误: {str(e)}")
            return []

    @staticmethod
    def get_department_by_id(department_id):
        """
        根据ID获取部门
        :param department_id: 部门ID
        :return: 部门信息
        """
        try:
            department = Department.query.get(department_id)
            if not department:
                return None, "部门不存在"
            
            department_dict = department.to_dict()
            if not department_dict:
                return None, "部门数据转换失败"
                
            return department_dict, None
        except Exception as e:
            print(f"获取部门详情错误: department_id={department_id}, error={str(e)}")
            return None, str(e)

    @staticmethod
    def create_department(data):
        """
        创建部门
        :param data: 部门数据
        :return: 创建的部门信息
        """
        try:
            department = Department(**data)
            db.session.add(department)
            db.session.commit()
            
            department_dict = department.to_dict()
            if not department_dict:
                return None, "部门数据转换失败"
                
            return department_dict, None
        except Exception as e:
            db.session.rollback()
            print(f"创建部门错误: data={data}, error={str(e)}")
            return None, str(e)

    @staticmethod
    def update_department(department_id, data):
        """
        更新部门
        :param department_id: 部门ID
        :param data: 更新的数据
        :return: 更新后的部门信息
        """
        try:
            department = Department.query.get(department_id)
            if not department:
                return None, "部门不存在"
            
            for key, value in data.items():
                setattr(department, key, value)
            
            db.session.commit()
            
            department_dict = department.to_dict()
            if not department_dict:
                return None, "部门数据转换失败"
                
            return department_dict, None
        except Exception as e:
            db.session.rollback()
            print(f"更新部门错误: department_id={department_id}, data={data}, error={str(e)}")
            return None, str(e)

    @staticmethod
    def delete_department(department_id):
        """
        删除部门
        :param department_id: 部门ID
        :return: 是否成功
        """
        try:
            department = Department.query.get(department_id)
            if not department:
                return False, "部门不存在"
            
            db.session.delete(department)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"删除部门错误: department_id={department_id}, error={str(e)}")
            return False, str(e)

    @staticmethod
    def get_total_count():
        """获取部门总数"""
        return Department.query.filter_by(is_deleted=False).count()
