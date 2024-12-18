from datetime import datetime
from sqlalchemy import and_
from app import db
from app.models.attendance import Overtime
from app.models.employee import Employee

class OvertimeService:
    @staticmethod
    def get_overtimes(employee_id=None, status=None):
        """获取加班记录列表
        
        Args:
            employee_id: 员工ID，如果提供则只返回该员工的加班记录
            status: 加班状态，如果提供则只返回指定状态的记录
            
        Returns:
            list: 加班记录列表
        """
        query = Overtime.query
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Overtime.created_at.desc()).all()

    @staticmethod
    def get_overtime(overtime_id):
        """获取单个加班记录
        
        Args:
            overtime_id: 加班记录ID
            
        Returns:
            Overtime: 加班记录对象
        """
        return Overtime.query.get(overtime_id)

    @staticmethod
    def create_overtime(overtime_data):
        """创建加班记录
        
        Args:
            overtime_data: 加班数据字典
            
        Returns:
            Overtime: 创建的加班记录对象
        """
        # 转换日期时间字符串为datetime对象
        if isinstance(overtime_data.get('start_time'), str):
            overtime_data['start_time'] = datetime.strptime(overtime_data['start_time'], '%Y-%m-%d %H:%M:%S')
        if isinstance(overtime_data.get('end_time'), str):
            overtime_data['end_time'] = datetime.strptime(overtime_data['end_time'], '%Y-%m-%d %H:%M:%S')
            
        overtime = Overtime(**overtime_data)
        db.session.add(overtime)
        db.session.commit()
        return overtime

    @staticmethod
    def update_overtime(overtime_id, overtime_data):
        """更新加班记录
        
        Args:
            overtime_id: 加班记录ID
            overtime_data: 加班数据字典
            
        Returns:
            Overtime: 更新后的加班记录对象
        """
        overtime = Overtime.query.get(overtime_id)
        if overtime:
            # 转换日期时间字符串为datetime对象
            if 'start_time' in overtime_data and isinstance(overtime_data['start_time'], str):
                overtime_data['start_time'] = datetime.strptime(overtime_data['start_time'], '%Y-%m-%d %H:%M:%S')
            if 'end_time' in overtime_data and isinstance(overtime_data['end_time'], str):
                overtime_data['end_time'] = datetime.strptime(overtime_data['end_time'], '%Y-%m-%d %H:%M:%S')
                
            for key, value in overtime_data.items():
                setattr(overtime, key, value)
            db.session.commit()
        return overtime

    @staticmethod
    def delete_overtime(overtime_id):
        """删除加班记录
        
        Args:
            overtime_id: 加班记录ID
            
        Returns:
            bool: 是否删除成功
        """
        overtime = Overtime.query.get(overtime_id)
        if overtime:
            db.session.delete(overtime)
            db.session.commit()
            return True
        return False

    @staticmethod
    def approve_overtime(overtime_id, approved_by, status='approved'):
        """审批加班申请
        
        Args:
            overtime_id: 加班记录ID
            approved_by: 审批人ID
            status: 审批状态(approved/rejected)
            
        Returns:
            Overtime: 更新后的加班记录对象
        """
        overtime = Overtime.query.get(overtime_id)
        if overtime:
            overtime.status = status
            overtime.approved_by = approved_by
            overtime.updated_at = datetime.utcnow()
            db.session.commit()
        return overtime

    @staticmethod
    def get_employee_overtimes_in_date_range(employee_id, start_date, end_date):
        """获取员工在指定日期范围内的加班记录
        
        Args:
            employee_id: 员工ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 加班记录列表
        """
        return Overtime.query.filter(
            and_(
                Overtime.employee_id == employee_id,
                Overtime.start_time <= end_date,
                Overtime.end_time >= start_date,
                Overtime.status == 'approved'
            )
        ).all()
