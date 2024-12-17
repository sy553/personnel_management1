from flask import Blueprint, request, jsonify
from app.models.attendance import Attendance, Leave, Overtime
from app.models.employee import Employee
from app import db
from datetime import datetime, timedelta, time
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('attendance', __name__, url_prefix='/api')

@bp.route('/attendance', methods=['GET'])
def get_attendance_records():
    """获取考勤记录列表"""
    try:
        # 支持按员工ID、日期范围和考勤状态筛选
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')  # 格式：YYYY-MM-DD
        end_date = request.args.get('end_date')  # 格式：YYYY-MM-DD
        status = request.args.get('status')  # 考勤状态：normal, late, early, absent
        
        query = Attendance.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d'))
        if status:
            query = query.filter_by(status=status)
            
        records = query.order_by(Attendance.date.desc()).all()
        return jsonify({
            'code': 200,
            'data': [record.to_dict() for record in records],
            'msg': '获取考勤记录列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取考勤记录列表失败: {str(e)}'
        })

@bp.route('/attendance/<int:id>', methods=['GET'])
def get_attendance_record(id):
    """获取单个考勤记录"""
    try:
        record = Attendance.query.get(id)
        if not record:
            return jsonify({
                'code': 404,
                'msg': '考勤记录不存在'
            })
        return jsonify({
            'code': 200,
            'data': record.to_dict(),
            'msg': '获取考勤记录成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取考勤记录失败: {str(e)}'
        })

@bp.route('/attendance', methods=['POST'])
def create_attendance_record():
    """创建考勤记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['employee_id', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
                
        # 验证员工是否存在
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({
                'code': 404,
                'msg': '员工不存在'
            })
            
        # 检查是否已有当天考勤记录
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        existing_record = Attendance.query.filter_by(
            employee_id=data['employee_id'],
            date=date
        ).first()
        
        if existing_record:
            # 如果已有记录，更新签退时间
            if 'check_out' in data:
                existing_record.check_out = datetime.combine(
                    date,
                    datetime.strptime(data['check_out'], '%H:%M').time()
                )
                db.session.commit()
                return jsonify({
                    'code': 200,
                    'msg': '签退成功',
                    'data': existing_record.to_dict()
                })
            return jsonify({
                'code': 400,
                'msg': '该员工当天已有考勤记录'
            })
            
        # 创建新的考勤记录
        record = Attendance(
            employee_id=data['employee_id'],
            date=date,
            check_in=datetime.combine(
                date,
                datetime.strptime(data['check_in'], '%H:%M').time()
            ) if 'check_in' in data else None,
            check_out=datetime.combine(
                date,
                datetime.strptime(data['check_out'], '%H:%M').time()
            ) if 'check_out' in data else None,
            status='normal'  # 初始状态设为正常
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '考勤记录创建成功',
            'data': record.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建考勤记录失败: {str(e)}'
        })

@bp.route('/attendance/<int:id>', methods=['PUT'])
def update_attendance_record(id):
    """更新考勤记录"""
    try:
        record = Attendance.query.get(id)
        if not record:
            return jsonify({
                'code': 404,
                'msg': '考勤记录不存在'
            })
            
        data = request.get_json()
        
        # 更新字段
        if 'check_in_time' in data:
            record.check_in_time = datetime.strptime(data['check_in_time'], '%H:%M:%S').time()
        if 'check_out_time' in data:
            record.check_out_time = datetime.strptime(data['check_out_time'], '%H:%M:%S').time()
        if 'status' in data:
            record.status = data['status']
        if 'remarks' in data:
            record.remarks = data['remarks']
            
        # 重新计算考勤状态（如果没有手动指定）
        if 'status' not in data:
            standard_check_in = datetime.strptime('09:00:00', '%H:%M:%S').time()
            standard_check_out = datetime.strptime('18:00:00', '%H:%M:%S').time()
            
            if record.check_in_time > standard_check_in:
                record.status = 'late'
            elif record.check_out_time and record.check_out_time < standard_check_out:
                record.status = 'early'
            else:
                record.status = 'normal'
                
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': record.to_dict(),
            'msg': '更新考勤记录成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'更新考勤记录失败: {str(e)}'
        })

@bp.route('/attendance/<int:id>', methods=['DELETE'])
def delete_attendance_record(id):
    """删除考勤记录"""
    try:
        record = Attendance.query.get(id)
        if not record:
            return jsonify({
                'code': 404,
                'msg': '考勤记录不存在'
            })
            
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除考勤记录成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'删除考勤记录失败: {str(e)}'
        })

@bp.route('/attendance/statistics', methods=['GET'])
def get_attendance_statistics():
    """获取考勤统计数据
    
    支持按部门和日期范围筛选
    返回考勤率、迟到早退、缺勤等统计数据
    """
    try:
        # 获取查询参数
        department_id = request.args.get('department_id', type=int)
        start_date = request.args.get('start_date')  # 格式：YYYY-MM-DD
        end_date = request.args.get('end_date')  # 格式：YYYY-MM-DD
        
        if not start_date or not end_date:
            return jsonify({
                'code': 400,
                'msg': '开始日期和结束日期不能为空'
            })
            
        # 转换日期字符串为datetime对象
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 计算日期范围内的工作日数量（不包括周末）
        total_days = sum(1 for date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1))
                        if date.weekday() < 5)  # 0-4 表示周一至周五
        
        # 构建基础查询
        query = db.session.query(
            Employee,
            db.func.count(Attendance.id).label('total_records'),
            # 正常出勤次数
            db.func.sum(
                db.case(
                    (Attendance.status == 'normal', 1),
                    else_=0
                )
            ).label('normal_count'),
            # 迟到次数
            db.func.sum(
                db.case(
                    (Attendance.status == 'late', 1),
                    else_=0
                )
            ).label('late_count'),
            # 早退次数
            db.func.sum(
                db.case(
                    (Attendance.status == 'early', 1),
                    else_=0
                )
            ).label('early_count'),
            # 缺勤次数
            db.func.sum(
                db.case(
                    (Attendance.status == 'absent', 1),
                    else_=0
                )
            ).label('absent_count')
        ).outerjoin(
            Attendance,
            db.and_(
                Employee.id == Attendance.employee_id,
                Attendance.date.between(start_date, end_date)
            )
        )
        
        # 添加部门筛选
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        # 按员工分组
        query = query.group_by(Employee.id)
        
        # 执行查询
        results = query.all()
        
        # 处理统计结果
        total_employees = len(results)
        total_attendance = sum(r.normal_count or 0 for r in results)
        total_late = sum(r.late_count or 0 for r in results)
        total_early = sum(r.early_count or 0 for r in results)
        total_absent = sum(r.absent_count or 0 for r in results)
        
        # 计算出勤率
        expected_attendance = total_employees * total_days
        attendance_rate = total_attendance / expected_attendance if expected_attendance > 0 else 0
        
        # 准备详细数据
        details = []
        for r in results:
            employee = r[0]  # Employee对象
            attended_days = (r.normal_count or 0)
            details.append({
                'id': employee.id,
                'employee_name': employee.name,
                'department_name': employee.department.name if employee.department else None,
                'total_days': total_days,
                'attended_days': attended_days,
                'late_count': r.late_count or 0,
                'early_count': r.early_count or 0,
                'absent_count': r.absent_count or 0,
                'attendance_rate': attended_days / total_days if total_days > 0 else 0
            })
        
        return jsonify({
            'code': 200,
            'msg': '获取统计数据成功',
            'data': {
                'totalDays': total_days,
                'totalEmployees': total_employees,
                'attendanceRate': attendance_rate,
                'lateCount': total_late,
                'earlyCount': total_early,
                'absentCount': total_absent,
                'details': details
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取统计数据失败: {str(e)}'
        })

# 请假相关API
@bp.route('/leave', methods=['GET'])
@jwt_required()
def get_leave_records():
    """获取请假记录列表
    
    支持按员工ID、日期范围和状态筛选
    普通员工只能查看自己的请假记录
    管理员可以查看所有人的请假记录
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = Employee.query.get(current_user_id)
        
        # 获取查询参数
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')  # 格式：YYYY-MM-DD
        end_date = request.args.get('end_date')  # 格式：YYYY-MM-DD
        status = request.args.get('status')  # 状态：pending/approved/rejected
        
        # 构建查询
        query = Leave.query
        
        # 权限控制：普通员工只能查看自己的记录
        if not current_user.is_admin:
            query = query.filter_by(employee_id=current_user_id)
        elif employee_id:  # 管理员可以按员工ID筛选
            query = query.filter_by(employee_id=employee_id)
            
        # 应用其他过滤条件
        if start_date:
            query = query.filter(Leave.start_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Leave.end_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        if status:
            query = query.filter_by(status=status)
            
        records = query.order_by(Leave.created_at.desc()).all()
        return jsonify({
            'code': 200,
            'data': [record.to_dict() for record in records],
            'msg': '获取请假记录列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取请假记录列表失败: {str(e)}'
        })

@bp.route('/leave', methods=['POST'])
@jwt_required()
def create_leave_request():
    """创建请假申请
    
    必填字段：leave_type, start_date, end_date
    可选字段：reason
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['leave_type', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
                
        # 创建请假记录
        leave = Leave(
            employee_id=current_user_id,
            leave_type=data['leave_type'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S'),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S'),
            reason=data.get('reason', ''),
            status='pending'
        )
        
        db.session.add(leave)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': leave.to_dict(),
            'msg': '创建请假申请成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建请假申请失败: {str(e)}'
        })

@bp.route('/leave/<int:id>/approve', methods=['POST'])
@jwt_required()
def approve_leave_request(id):
    """审批请假申请
    
    只有管理员可以审批请假申请
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = Employee.query.get(current_user_id)
        
        # 验证权限
        if not current_user.is_admin:
            return jsonify({
                'code': 403,
                'msg': '没有权限审批请假申请'
            })
            
        leave = Leave.query.get(id)
        if not leave:
            return jsonify({
                'code': 404,
                'msg': '请假申请不存在'
            })
            
        data = request.get_json()
        status = data.get('status')
        if status not in ['approved', 'rejected']:
            return jsonify({
                'code': 400,
                'msg': '无效的审批状态'
            })
            
        leave.status = status
        leave.approved_by = current_user_id
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': leave.to_dict(),
            'msg': f'请假申请{status}成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'审批请假申请失败: {str(e)}'
        })

# 加班相关API
@bp.route('/overtime', methods=['GET'])
@jwt_required()
def get_overtime_records():
    """获取加班记录列表
    
    支持按员工ID、日期范围和状态筛选
    普通员工只能查看自己的加班记录
    管理员可以查看所有人的加班记录
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = Employee.query.get(current_user_id)
        
        # 获取查询参数
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')  # 格式：YYYY-MM-DD
        end_date = request.args.get('end_date')  # 格式：YYYY-MM-DD
        status = request.args.get('status')  # 状态：pending/approved/rejected
        
        # 构建查询
        query = Overtime.query
        
        # 权限控制：普通员工只能查看自己的记录
        if not current_user.is_admin:
            query = query.filter_by(employee_id=current_user_id)
        elif employee_id:  # 管理员可以按员工ID筛选
            query = query.filter_by(employee_id=employee_id)
            
        # 应用其他过滤条件
        if start_date:
            query = query.filter(Overtime.start_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Overtime.end_time <= datetime.strptime(end_date, '%Y-%m-%d'))
        if status:
            query = query.filter_by(status=status)
            
        records = query.order_by(Overtime.created_at.desc()).all()
        return jsonify({
            'code': 200,
            'data': [record.to_dict() for record in records],
            'msg': '获取加班记录列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取加班记录列表失败: {str(e)}'
        })

@bp.route('/overtime', methods=['POST'])
@jwt_required()
def create_overtime_request():
    """创建加班申请
    
    必填字段：start_time, end_time
    可选字段：reason
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
                
        # 创建加班记录
        overtime = Overtime(
            employee_id=current_user_id,
            start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
            reason=data.get('reason', ''),
            status='pending'
        )
        
        db.session.add(overtime)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': overtime.to_dict(),
            'msg': '创建加班申请成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建加班申请失败: {str(e)}'
        })

@bp.route('/overtime/<int:id>/approve', methods=['POST'])
@jwt_required()
def approve_overtime_request(id):
    """审批加班申请
    
    只有管理员可以审批加班申请
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = Employee.query.get(current_user_id)
        
        # 验证权限
        if not current_user.is_admin:
            return jsonify({
                'code': 403,
                'msg': '没有权限审批加班申请'
            })
            
        overtime = Overtime.query.get(id)
        if not overtime:
            return jsonify({
                'code': 404,
                'msg': '加班申请不存在'
            })
            
        data = request.get_json()
        status = data.get('status')
        if status not in ['approved', 'rejected']:
            return jsonify({
                'code': 400,
                'msg': '无效的审批状态'
            })
            
        overtime.status = status
        overtime.approved_by = current_user_id
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': overtime.to_dict(),
            'msg': f'加班申请{status}成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'审批加班申请失败: {str(e)}'
        })
