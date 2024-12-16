from app import db
from app.models import Position, Employee
from sqlalchemy import or_
from datetime import datetime

class PositionService:
    @staticmethod
    def get_positions():
        """
        获取所有职位列表
        :return: 职位列表
        """
        try:
            positions = Position.query.order_by(Position.id).all()
            return positions
        except Exception as e:
            print(f"获取职位列表错误: {str(e)}")
            return []

    @staticmethod
    def get_position(position_id):
        """
        获取单个职位信息
        :param position_id: 职位ID
        :return: (职位对象, 错误信息)
        """
        try:
            position = Position.query.get(position_id)
            if not position:
                return None, "职位不存在"
            return position, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_position_by_id(position_id):
        """
        根据ID获取职位
        :param position_id: 职位ID
        :return: 职位信息
        """
        try:
            position = Position.query.get(position_id)
            if not position:
                return None, "职位不存在"
            
            position_dict = position.to_dict()
            if not position_dict:
                return None, "职位数据转换失败"
                
            return position_dict, None
        except Exception as e:
            print(f"获取职位详情错误: position_id={position_id}, error={str(e)}")
            return None, str(e)

    @staticmethod
    def create_position(data):
        """
        创建职位
        :param data: 职位数据
        :return: 创建的职位信息
        """
        try:
            position = Position(**data)
            db.session.add(position)
            db.session.commit()
            
            position_dict = position.to_dict()
            if not position_dict:
                return None, "职位数据转换失败"
                
            return position_dict, None
        except Exception as e:
            db.session.rollback()
            print(f"创建职位错误: data={data}, error={str(e)}")
            return None, str(e)

    @staticmethod
    def update_position(position_id, data):
        """
        更新职位
        :param position_id: 职位ID
        :param data: 更新的数据
        :return: 更新后的职位信息
        """
        try:
            position = Position.query.get(position_id)
            if not position:
                return None, "职位不存在"
            
            for key, value in data.items():
                setattr(position, key, value)
            
            db.session.commit()
            
            position_dict = position.to_dict()
            if not position_dict:
                return None, "职位数据转换失败"
                
            return position_dict, None
        except Exception as e:
            db.session.rollback()
            print(f"更新职位错误: position_id={position_id}, data={data}, error={str(e)}")
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
            
            # 检查是否有任何员工（包括非在职）关联到该职位
            employees = Employee.query.filter_by(position_id=position_id).all()
            if employees:
                # 检查在职员工
                active_employees = [emp for emp in employees if emp.employment_status == 'active']
                if active_employees:
                    active_names = ', '.join([emp.name for emp in active_employees])
                    return False, f"该职位下还有{len(active_employees)}名在职员工（{active_names}），无法删除"
                
                # 如果只有非在职员工，将这些员工的position_id设为None
                for emp in employees:
                    emp.position_id = None
                    
            db.session.delete(position)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"删除职位错误: position_id={position_id}, error={str(e)}")
            return False, str(e)

    @staticmethod
    def get_employee_distribution():
        """获取各职位员工数量分布"""
        positions = Position.query.filter_by(is_deleted=False).all()
        stats = []
        for pos in positions:
            employee_count = Employee.query.filter_by(
                position_id=pos.id,
                is_deleted=False
            ).count()
            stats.append({
                'name': pos.name,
                'value': employee_count
            })
        return stats
