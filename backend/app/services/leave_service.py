from datetime import datetime
from sqlalchemy import and_
from app import db
from app.models.attendance import Leave
from app.models.employee import Employee

class LeaveService:
    @staticmethod
    def get_leaves(employee_id=None, status=None):
        """获取请假记录列表
        
        Args:
            employee_id: 员工ID，如果提供则只返回该员工的请假记录
            status: 请假状态，如果提供则只返回指定状态的记录
            
        Returns:
            list: 请假记录列表
        """
        query = Leave.query
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Leave.created_at.desc()).all()

    @staticmethod
    def get_leave(leave_id):
        """获取单个请假记录
        
        Args:
            leave_id: 请假记录ID
            
        Returns:
            Leave: 请假记录对象
        """
        return Leave.query.get(leave_id)

    @staticmethod
    def create_leave(leave_data):
        """创建请假记录
        
        Args:
            leave_data: 请假数据字典
            
        Returns:
            Leave: 创建的请假记录对象
        """
        # 转换日期时间字符串为datetime对象
        if isinstance(leave_data.get('start_date'), str):
            leave_data['start_date'] = datetime.strptime(leave_data['start_date'], '%Y-%m-%d %H:%M:%S')
        if isinstance(leave_data.get('end_date'), str):
            leave_data['end_date'] = datetime.strptime(leave_data['end_date'], '%Y-%m-%d %H:%M:%S')
            
        leave = Leave(**leave_data)
        db.session.add(leave)
        db.session.commit()
        return leave

    @staticmethod
    def update_leave(leave_id, leave_data):
        """更新请假记录
        
        Args:
            leave_id: 请假记录ID
            leave_data: 请假数据字典
            
        Returns:
            Leave: 更新后的请假记录对象
        """
        leave = Leave.query.get(leave_id)
        if leave:
            # 转换日期时间字符串为datetime对象
            if 'start_date' in leave_data and isinstance(leave_data['start_date'], str):
                leave_data['start_date'] = datetime.strptime(leave_data['start_date'], '%Y-%m-%d %H:%M:%S')
            if 'end_date' in leave_data and isinstance(leave_data['end_date'], str):
                leave_data['end_date'] = datetime.strptime(leave_data['end_date'], '%Y-%m-%d %H:%M:%S')
                
            for key, value in leave_data.items():
                setattr(leave, key, value)
            db.session.commit()
        return leave

    @staticmethod
    def delete_leave(leave_id):
        """删除请假记录
        
        Args:
            leave_id: 请假记录ID
            
        Returns:
            bool: 是否删除成功
        """
        leave = Leave.query.get(leave_id)
        if leave:
            db.session.delete(leave)
            db.session.commit()
            return True
        return False

    @staticmethod
    def approve_leave(leave_id, approved_by, status='approved'):
        """审批请假申请
        
        Args:
            leave_id: 请假记录ID
            approved_by: 审批人ID
            status: 审批状态(approved/rejected)
            
        Returns:
            Leave: 更新后的请假记录对象
        """
        leave = Leave.query.get(leave_id)
        if leave:
            leave.status = status
            leave.approved_by = approved_by
            leave.updated_at = datetime.utcnow()
            db.session.commit()
        return leave

    @staticmethod
    def get_employee_leaves_in_date_range(employee_id, start_date, end_date):
        """获取员工在指定日期范围内的请假记录
        
        Args:
            employee_id: 员工ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 请假记录列表
        """
        return Leave.query.filter(
            and_(
                Leave.employee_id == employee_id,
                Leave.start_date <= end_date,
                Leave.end_date >= start_date,
                Leave.status == 'approved'
            )
        ).all()
