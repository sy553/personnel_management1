from flask import Blueprint, request, jsonify
from app.models.attendance import Attendance
from app.models.employee import Employee
from app import db
from datetime import datetime, timedelta

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
        required_fields = ['employee_id', 'date', 'check_in_time']
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
            return jsonify({
                'code': 400,
                'msg': '该员工当天已有考勤记录'
            })
            
        # 计算考勤状态
        check_in_time = datetime.strptime(data['check_in_time'], '%H:%M:%S').time()
        check_out_time = datetime.strptime(data.get('check_out_time', '18:00:00'), '%H:%M:%S').time() if data.get('check_out_time') else None
        standard_check_in = datetime.strptime('09:00:00', '%H:%M:%S').time()
        standard_check_out = datetime.strptime('18:00:00', '%H:%M:%S').time()
        
        if check_in_time > standard_check_in:
            status = 'late'
        elif check_out_time and check_out_time < standard_check_out:
            status = 'early'
        else:
            status = 'normal'
            
        record = Attendance(
            employee_id=data['employee_id'],
            date=date,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status=status,
            remarks=data.get('remarks', '')
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
    """获取考勤统计"""
    try:
        # 支持按员工ID和月份筛选
        employee_id = request.args.get('employee_id', type=int)
        month = request.args.get('month')  # 格式：YYYY-MM
        
        if not month:
            return jsonify({
                'code': 400,
                'msg': '月份参数不能为空'
            })
            
        # 解析月份
        year, month = map(int, month.split('-'))
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
        # 构建查询
        query = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        )
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
            
        records = query.all()
        
        # 统计数据
        statistics = {
            'total': len(records),
            'normal': len([r for r in records if r.status == 'normal']),
            'late': len([r for r in records if r.status == 'late']),
            'early': len([r for r in records if r.status == 'early']),
            'absent': len([r for r in records if r.status == 'absent'])
        }
        
        return jsonify({
            'code': 200,
            'data': statistics,
            'msg': '获取考勤统计成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取考勤统计失败: {str(e)}'
        })
