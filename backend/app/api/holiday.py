"""
假期管理相关API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from sqlalchemy import and_, or_
from app.models.holiday import HolidayType, HolidayRequest, HolidayBalance
from app.models.employee import Employee
from app.models.user import User
from app import db
from app.utils.validators import validate_date_range
from app.utils.auth import admin_required

bp = Blueprint('holiday', __name__, url_prefix='/api/holiday')

@bp.route('/types', methods=['GET'])
@jwt_required()
def get_holiday_types():
    """获取假期类型列表
    
    权限：
        - 所有用户都可以查看
        
    返回：
        - 成功: {'code': 200, 'data': [假期类型列表], 'msg': 'success'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        # 获取查询参数
        is_active = request.args.get('is_active', type=bool, default=True)
        
        # 查询假期类型
        query = HolidayType.query
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        holiday_types = query.all()
        return jsonify({
            'code': 200,
            'data': [ht.to_dict() for ht in holiday_types],
            'msg': 'success'
        })
    except Exception as e:
        current_app.logger.error(f'获取假期类型列表失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/types', methods=['POST'])
@jwt_required()
@admin_required
def create_holiday_type():
    """创建假期类型
    
    权限：
        - 仅管理员可以创建
        
    请求体：
        {
            'name': 假期类型名称,
            'code': 假期类型代码,
            'annual_quota': 年度配额,
            'min_duration': 最小请假时长,
            'max_duration': 最大请假时长,
            'requires_proof': 是否需要证明材料,
            'description': 描述
        }
        
    返回：
        - 成功: {'code': 200, 'data': 假期类型信息, 'msg': '创建成功'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'code']
        for field in required_fields:
            if field not in data:
                return jsonify({'code': 400, 'msg': f'缺少必填字段: {field}'}), 400
        
        # 检查代码是否已存在
        if HolidayType.query.filter_by(code=data['code']).first():
            return jsonify({'code': 400, 'msg': '假期类型代码已存在'}), 400
        
        # 创建假期类型
        holiday_type = HolidayType(
            name=data['name'],
            code=data['code'],
            annual_quota=data.get('annual_quota'),
            min_duration=data.get('min_duration'),
            max_duration=data.get('max_duration'),
            requires_proof=data.get('requires_proof', False),
            description=data.get('description')
        )
        
        db.session.add(holiday_type)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday_type.to_dict(),
            'msg': '创建成功'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建假期类型失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/types/<int:type_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_holiday_type(type_id):
    """更新假期类型
    
    权限：
        - 仅管理员可以更新
        
    请求体：
        {
            'name': 假期类型名称,
            'annual_quota': 年度配额,
            'min_duration': 最小请假时长,
            'max_duration': 最大请假时长,
            'requires_proof': 是否需要证明材料,
            'description': 描述,
            'is_active': 是否启用
        }
        
    返回：
        - 成功: {'code': 200, 'data': 假期类型信息, 'msg': '更新成功'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        holiday_type = HolidayType.query.get(type_id)
        if not holiday_type:
            return jsonify({'code': 404, 'msg': '假期类型不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            holiday_type.name = data['name']
        if 'annual_quota' in data:
            holiday_type.annual_quota = data['annual_quota']
        if 'min_duration' in data:
            holiday_type.min_duration = data['min_duration']
        if 'max_duration' in data:
            holiday_type.max_duration = data['max_duration']
        if 'requires_proof' in data:
            holiday_type.requires_proof = data['requires_proof']
        if 'description' in data:
            holiday_type.description = data['description']
        if 'is_active' in data:
            holiday_type.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday_type.to_dict(),
            'msg': '更新成功'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新假期类型失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/requests', methods=['GET'])
@jwt_required()
def get_holiday_requests():
    """获取假期申请列表
    
    URL参数：
        - employee_id: 员工ID（可选）
        - status: 状态（可选）
        - start_date: 开始日期 (YYYY-MM-DD)（可选）
        - end_date: 结束日期 (YYYY-MM-DD)（可选）
        
    权限：
        - 普通用户只能查看自己的假期申请
        - 管理员可以查看所有人的假期申请
        
    返回：
        - 成功: {'code': 200, 'data': [假期申请列表], 'msg': 'success'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        # 获取当前用户
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({'code': 401, 'msg': '用户未登录'}), 401
        
        # 构建查询
        query = HolidayRequest.query
        
        # 如果不是管理员，只能查看自己的假期申请
        if not current_user.is_admin:
            query = query.filter_by(employee_id=current_user.employee.id)
        else:
            # 管理员可以按员工ID筛选
            employee_id = request.args.get('employee_id', type=int)
            if employee_id:
                query = query.filter_by(employee_id=employee_id)
        
        # 按状态筛选
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        # 按日期范围筛选
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(
                    or_(
                        and_(HolidayRequest.start_date >= start_date,
                             HolidayRequest.start_date <= end_date),
                        and_(HolidayRequest.end_date >= start_date,
                             HolidayRequest.end_date <= end_date)
                    )
                )
            except ValueError:
                return jsonify({'code': 400, 'msg': '日期格式错误'}), 400
        
        # 获取结果
        holiday_requests = query.order_by(HolidayRequest.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'data': [hr.to_dict() for hr in holiday_requests],
            'msg': 'success'
        })
    except Exception as e:
        current_app.logger.error(f'获取假期申请列表失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/requests', methods=['POST'])
@jwt_required()
def create_holiday_request():
    """创建假期申请
    
    请求体：
        {
            'holiday_type_id': 假期类型ID,
            'start_date': 开始日期 (YYYY-MM-DD),
            'end_date': 结束日期 (YYYY-MM-DD),
            'duration': 请假天数,
            'reason': 请假原因,
            'proof_url': 证明材料URL（可选）
        }
        
    返回：
        - 成功: {'code': 200, 'data': 假期申请信息, 'msg': '申请提交成功'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        # 获取当前用户
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.employee:
            return jsonify({'code': 401, 'msg': '用户未登录或不是员工'}), 401
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['holiday_type_id', 'start_date', 'end_date', 'duration', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({'code': 400, 'msg': f'缺少必填字段: {field}'}), 400
        
        # 验证假期类型
        holiday_type = HolidayType.query.get(data['holiday_type_id'])
        if not holiday_type:
            return jsonify({'code': 404, 'msg': '假期类型不存在'}), 404
        if not holiday_type.is_active:
            return jsonify({'code': 400, 'msg': '该假期类型已停用'}), 400
        
        # 验证日期
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            if start_date > end_date:
                return jsonify({'code': 400, 'msg': '开始日期不能晚于结束日期'}), 400
            if start_date < date.today():
                return jsonify({'code': 400, 'msg': '不能申请过去的日期'}), 400
        except ValueError:
            return jsonify({'code': 400, 'msg': '日期格式错误'}), 400
        
        # 验证请假时长
        duration = float(data['duration'])
        if holiday_type.min_duration and duration < holiday_type.min_duration:
            return jsonify({'code': 400, 'msg': f'请假时长不能少于{holiday_type.min_duration}天'}), 400
        if holiday_type.max_duration and duration > holiday_type.max_duration:
            return jsonify({'code': 400, 'msg': f'请假时长不能超过{holiday_type.max_duration}天'}), 400
        
        # 检查是否有足够的假期余额
        if holiday_type.annual_quota:
            balance = HolidayBalance.query.filter_by(
                employee_id=current_user.employee.id,
                holiday_type_id=holiday_type.id,
                year=date.today().year
            ).first()
            
            if not balance:
                # 创建新的假期余额记录
                balance = HolidayBalance(
                    employee_id=current_user.employee.id,
                    holiday_type_id=holiday_type.id,
                    year=date.today().year,
                    total_days=holiday_type.annual_quota,
                    used_days=0,
                    remaining_days=holiday_type.annual_quota
                )
                db.session.add(balance)
            
            if duration > balance.remaining_days:
                return jsonify({'code': 400, 'msg': f'假期余额不足，剩余{balance.remaining_days}天'}), 400
        
        # 创建假期申请
        holiday_request = HolidayRequest(
            employee_id=current_user.employee.id,
            holiday_type_id=holiday_type.id,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            reason=data['reason'],
            proof_url=data.get('proof_url'),
            status='pending'
        )
        
        db.session.add(holiday_request)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday_request.to_dict(),
            'msg': '申请提交成功'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建假期申请失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_holiday_request(request_id):
    """审批假期申请
    
    请求体：
        {
            'action': 'approve' 或 'reject',
            'comment': 审批意见
        }
        
    返回：
        - 成功: {'code': 200, 'data': 假期申请信息, 'msg': '审批成功'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        # 获取当前用户
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.employee:
            return jsonify({'code': 401, 'msg': '用户未登录或不是员工'}), 401
        
        # 获取假期申请
        holiday_request = HolidayRequest.query.get(request_id)
        if not holiday_request:
            return jsonify({'code': 404, 'msg': '假期申请不存在'}), 404
        
        # 检查申请状态
        if holiday_request.status != 'pending':
            return jsonify({'code': 400, 'msg': '该申请已经被处理'}), 400
        
        data = request.get_json()
        action = data.get('action')
        if action not in ['approve', 'reject']:
            return jsonify({'code': 400, 'msg': '无效的操作'}), 400
        
        # 更新申请状态
        holiday_request.status = 'approved' if action == 'approve' else 'rejected'
        holiday_request.approver_id = current_user.employee.id
        holiday_request.approval_time = datetime.utcnow()
        holiday_request.approval_comment = data.get('comment')
        
        # 如果批准申请，更新假期余额
        if action == 'approve' and holiday_request.holiday_type.annual_quota:
            balance = HolidayBalance.query.filter_by(
                employee_id=holiday_request.employee_id,
                holiday_type_id=holiday_request.holiday_type_id,
                year=holiday_request.start_date.year
            ).first()
            
            if balance:
                balance.used_days += holiday_request.duration
                balance.remaining_days = balance.total_days - balance.used_days
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday_request.to_dict(),
            'msg': '审批成功'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'审批假期申请失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/requests/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_holiday_request(request_id):
    """取消假期申请
    
    权限：
        - 只能取消自己的申请
        - 只能取消待审批的申请
        
    返回：
        - 成功: {'code': 200, 'data': 假期申请信息, 'msg': '取消成功'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        # 获取当前用户
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.employee:
            return jsonify({'code': 401, 'msg': '用户未登录或不是员工'}), 401
        
        # 获取假期申请
        holiday_request = HolidayRequest.query.get(request_id)
        if not holiday_request:
            return jsonify({'code': 404, 'msg': '假期申请不存在'}), 404
        
        # 检查权限
        if holiday_request.employee_id != current_user.employee.id:
            return jsonify({'code': 403, 'msg': '无权取消他人的申请'}), 403
        
        # 检查状态
        if holiday_request.status != 'pending':
            return jsonify({'code': 400, 'msg': '只能取消待审批的申请'}), 400
        
        # 更新状态
        holiday_request.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday_request.to_dict(),
            'msg': '取消成功'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'取消假期申请失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500

@bp.route('/balances', methods=['GET'])
@jwt_required()
def get_holiday_balances():
    """获取假期余额
    
    URL参数：
        - employee_id: 员工ID（可选，管理员可查询指定员工）
        - year: 年份（可选，默认当前年份）
        
    权限：
        - 普通用户只能查看自己的假期余额
        - 管理员可以查看所有人的假期余额
        
    返回：
        - 成功: {'code': 200, 'data': [假期余额列表], 'msg': 'success'}
        - 失败: {'code': 4xx/5xx, 'msg': 错误信息}
    """
    try:
        # 获取当前用户
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.employee:
            return jsonify({'code': 401, 'msg': '用户未登录或不是员工'}), 401
        
        # 构建查询
        query = HolidayBalance.query
        
        # 如果不是管理员，只能查看自己的假期余额
        if not current_user.is_admin:
            query = query.filter_by(employee_id=current_user.employee.id)
        else:
            # 管理员可以按员工ID筛选
            employee_id = request.args.get('employee_id', type=int)
            if employee_id:
                query = query.filter_by(employee_id=employee_id)
        
        # 按年份筛选
        year = request.args.get('year', type=int, default=date.today().year)
        query = query.filter_by(year=year)
        
        # 获取结果
        balances = query.all()
        
        return jsonify({
            'code': 200,
            'data': [balance.to_dict() for balance in balances],
            'msg': 'success'
        })
    except Exception as e:
        current_app.logger.error(f'获取假期余额失败: {str(e)}')
        return jsonify({'code': 500, 'msg': '系统错误'}), 500
