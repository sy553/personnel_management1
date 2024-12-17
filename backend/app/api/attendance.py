from flask import Blueprint, request, jsonify
from app.models.attendance import Attendance, Leave, Overtime, AttendanceRule
from app.models.employee import Employee
from app.models.user import User  # 添加User模型的导入
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

def get_attendance_status(check_time, rule):
    """根据考勤规则判断考勤状态"""
    if not check_time:
        return 'absent'  # 缺勤
        
    check_time = check_time.time()
    late_threshold = timedelta(minutes=rule.late_threshold)
    early_threshold = timedelta(minutes=rule.early_leave_threshold)
    
    # 判断迟到
    if check_time > (datetime.combine(datetime.today(), rule.work_start_time) + late_threshold).time():
        return 'late'
    # 判断早退
    elif check_time < (datetime.combine(datetime.today(), rule.work_end_time) - early_threshold).time():
        return 'early'
    else:
        return 'normal'

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
        
        # 获取默认考勤规则
        rule = AttendanceRule.query.filter_by(is_default=True).first()
        if not rule:
            return jsonify({
                'code': 500,
                'msg': '未找到默认考勤规则'
            })
        
        if existing_record:
            # 如果已有记录，更新签退时间
            if 'check_out' in data:
                check_out_time = datetime.strptime(data['check_out'], '%H:%M')
                existing_record.check_out = datetime.combine(date, check_out_time.time())
                # 更新考勤状态
                if existing_record.check_in:
                    existing_record.status = get_attendance_status(existing_record.check_out, rule)
            db.session.commit()
            return jsonify({
                'code': 200,
                'data': existing_record.to_dict(),
                'msg': '更新考勤记录成功'
            })
        else:
            # 创建新记录
            check_in_time = None
            if 'check_in' in data:
                check_in_time = datetime.strptime(data['check_in'], '%H:%M')
                check_in_time = datetime.combine(date, check_in_time.time())
                
            check_out_time = None
            if 'check_out' in data:
                check_out_time = datetime.strptime(data['check_out'], '%H:%M')
                check_out_time = datetime.combine(date, check_out_time.time())
            
            # 根据考勤规则判断状态
            status = get_attendance_status(check_in_time, rule)
            
            record = Attendance(
                employee_id=data['employee_id'],
                date=date,
                check_in=check_in_time,
                check_out=check_out_time,
                status=status,
                remark=data.get('remark')
            )
            
            db.session.add(record)
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'data': record.to_dict(),
                'msg': '创建考勤记录成功'
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
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({
                'code': 401,
                'msg': '用户未登录或不存在'
            })

        # 获取查询参数
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        query = Leave.query
        
        # 权限控制：普通员工只能查看自己的请假记录
        if current_user.role != 'admin':
            current_employee = Employee.query.filter_by(user_id=current_user_id).first()
            if not current_employee:
                return jsonify({
                    'code': 404,
                    'msg': '未找到员工信息'
                })
            query = query.filter_by(employee_id=current_employee.id)
        elif employee_id:  # 管理员可以按员工ID筛选
            query = query.filter_by(employee_id=employee_id)
            
        # 日期范围筛选
        if start_date:
            query = query.filter(Leave.start_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Leave.end_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
            
        records = query.order_by(Leave.created_at.desc()).all()
        return jsonify({
            'code': 200,
            'data': [record.to_dict() for record in records],
            'msg': '获取请假记录成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取请假记录失败: {str(e)}'
        })

@bp.route('/leave', methods=['POST'])
@jwt_required()
def create_leave_request():
    """创建请假申请
    
    必填字段：leave_type, start_date, end_date
    可选字段：reason
    
    日期格式支持：
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM:SS
    """
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_employee = Employee.query.filter_by(user_id=current_user_id).first()
        
        if not current_employee:
            return jsonify({
                'code': 404,
                'msg': '未找到员工信息'
            })
            
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['leave_type', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
                
        # 处理日期格式
        try:
            # 尝试解析完整的日期时间格式
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # 如果失败，尝试解析日期格式并设置时间为00:00:00
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '开始日期格式错误，请使用YYYY-MM-DD或YYYY-MM-DD HH:MM:SS'
                })
        
        try:
            # 尝试解析完整的日期时间格式
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # 如果失败，尝试解析日期格式并设置时间为23:59:59
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d') + timedelta(days=1, seconds=-1)
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '结束日期格式错误，请使用YYYY-MM-DD或YYYY-MM-DD HH:MM:SS'
                })
                
        # 创建请假记录
        leave = Leave(
            employee_id=current_employee.id,
            leave_type=data['leave_type'],
            start_date=start_date,
            end_date=end_date,
            reason=data.get('reason', '')
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
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({
                'code': 403,
                'msg': '没有权限进行此操作'
            })
            
        leave = Leave.query.get(id)
        if not leave:
            return jsonify({
                'code': 404,
                'msg': '请假记录不存在'
            })
            
        data = request.get_json()
        status = data.get('status')
        if status not in ['approved', 'rejected']:
            return jsonify({
                'code': 400,
                'msg': '无效的审批状态'
            })
            
        # 更新请假记录
        leave.status = status
        leave.approved_by = current_user_id
        leave.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': leave.to_dict(),
            'msg': '审批请假申请成功'
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
        current_user = User.query.get(current_user_id)
        
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
        current_user = User.query.get(current_user_id)
        
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

# 考勤规则相关API
@bp.route('/attendance-rules', methods=['GET'])
@jwt_required()
def get_attendance_rules():
    """获取考勤规则列表"""
    try:
        rules = AttendanceRule.query.all()
        return jsonify({
            'code': 200,
            'data': [rule.to_dict() for rule in rules],
            'msg': '获取考勤规则列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取考勤规则列表失败: {str(e)}'
        })

@bp.route('/attendance-rules/<int:id>', methods=['GET'])
@jwt_required()
def get_attendance_rule(id):
    """获取单个考勤规则"""
    try:
        rule = AttendanceRule.query.get(id)
        if not rule:
            return jsonify({
                'code': 404,
                'msg': '考勤规则不存在'
            })
        return jsonify({
            'code': 200,
            'data': rule.to_dict(),
            'msg': '获取考勤规则成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取考勤规则失败: {str(e)}'
        })

@bp.route('/attendance-rules', methods=['POST'])
@jwt_required()
def create_attendance_rule():
    """创建考勤规则"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['name', 'work_start_time', 'work_end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
        
        # 转换时间字符串为time对象
        try:
            work_start_time = datetime.strptime(data['work_start_time'], '%H:%M').time()
            work_end_time = datetime.strptime(data['work_end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'code': 400,
                'msg': '时间格式错误，请使用HH:MM格式'
            })
        
        # 如果设置为默认规则，先将其他规则的default设置为False
        if data.get('is_default'):
            AttendanceRule.query.filter_by(is_default=True).update({'is_default': False})
        
        # 创建新规则
        rule = AttendanceRule(
            name=data['name'],
            work_start_time=work_start_time,
            work_end_time=work_end_time,
            late_threshold=data.get('late_threshold', 15),
            early_leave_threshold=data.get('early_leave_threshold', 15),
            overtime_minimum=data.get('overtime_minimum', 60),
            is_default=data.get('is_default', False),
            description=data.get('description')
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': rule.to_dict(),
            'msg': '创建考勤规则成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建考勤规则失败: {str(e)}'
        })

@bp.route('/attendance-rules/<int:id>', methods=['PUT'])
@jwt_required()
def update_attendance_rule(id):
    """更新考勤规则"""
    try:
        rule = AttendanceRule.query.get(id)
        if not rule:
            return jsonify({
                'code': 404,
                'msg': '考勤规则不存在'
            })
        
        data = request.get_json()
        
        # 更新时间字段
        if 'work_start_time' in data:
            try:
                rule.work_start_time = datetime.strptime(data['work_start_time'], '%H:%M').time()
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '上班时间格式错误，请使用HH:MM格式'
                })
        
        if 'work_end_time' in data:
            try:
                rule.work_end_time = datetime.strptime(data['work_end_time'], '%H:%M').time()
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '下班时间格式错误，请使用HH:MM格式'
                })
        
        # 如果设置为默认规则，先将其他规则的default设置为False
        if data.get('is_default'):
            AttendanceRule.query.filter(AttendanceRule.id != id).update({'is_default': False})
        
        # 更新其他字段
        if 'name' in data:
            rule.name = data['name']
        if 'late_threshold' in data:
            rule.late_threshold = data['late_threshold']
        if 'early_leave_threshold' in data:
            rule.early_leave_threshold = data['early_leave_threshold']
        if 'overtime_minimum' in data:
            rule.overtime_minimum = data['overtime_minimum']
        if 'is_default' in data:
            rule.is_default = data['is_default']
        if 'description' in data:
            rule.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': rule.to_dict(),
            'msg': '更新考勤规则成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'更新考勤规则失败: {str(e)}'
        })

@bp.route('/attendance-rules/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_attendance_rule(id):
    """删除考勤规则"""
    try:
        rule = AttendanceRule.query.get(id)
        if not rule:
            return jsonify({
                'code': 404,
                'msg': '考勤规则不存在'
            })
        
        # 不允许删除默认规则
        if rule.is_default:
            return jsonify({
                'code': 400,
                'msg': '不能删除默认考勤规则'
            })
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除考勤规则成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'删除考勤规则失败: {str(e)}'
        })
