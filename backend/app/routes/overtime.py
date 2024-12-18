from flask import Blueprint, request, jsonify
from app.services.overtime_service import OvertimeService
from app.utils.auth import login_required
from flask_jwt_extended import get_jwt_identity
from app.models import User

# 创建蓝图
overtime_bp = Blueprint('overtime', __name__)

@overtime_bp.route('/overtimes', methods=['GET'])
@login_required
def get_overtimes():
    """获取加班记录列表"""
    try:
        # 获取查询参数
        employee_id = request.args.get('employee_id', type=int)
        status = request.args.get('status')
        
        # 获取加班记录
        overtimes = OvertimeService.get_overtimes(employee_id, status)
        return jsonify({
            'code': 200,
            'message': '获取加班记录成功',
            'data': [overtime.to_dict() for overtime in overtimes]
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取加班记录失败: {str(e)}'
        })

@overtime_bp.route('/overtimes/<int:overtime_id>', methods=['GET'])
@login_required
def get_overtime(overtime_id):
    """获取单个加班记录"""
    try:
        overtime = OvertimeService.get_overtime(overtime_id)
        if not overtime:
            return jsonify({
                'code': 404,
                'message': '加班记录不存在'
            })
        return jsonify({
            'code': 200,
            'message': '获取加班记录成功',
            'data': overtime.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取加班记录失败: {str(e)}'
        })

@overtime_bp.route('/overtimes', methods=['POST'])
@login_required
def create_overtime():
    """创建加班记录"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.employee:
            return jsonify({
                'code': 400,
                'message': '未找到员工信息'
            })
            
        data = request.get_json()
        data['employee_id'] = user.employee.id
        overtime = OvertimeService.create_overtime(data)
        return jsonify({
            'code': 200,
            'message': '创建加班记录成功',
            'data': overtime.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'创建加班记录失败: {str(e)}'
        })

@overtime_bp.route('/overtimes/<int:overtime_id>', methods=['PUT'])
@login_required
def update_overtime(overtime_id):
    """更新加班记录"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 401,
                'message': '未登录'
            })
            
        data = request.get_json()
        overtime = OvertimeService.get_overtime(overtime_id)
        
        if not overtime:
            return jsonify({
                'code': 404,
                'message': '加班记录不存在'
            })
            
        # 只允许本人或管理员修改
        if overtime.employee_id != user.employee.id and user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '无权修改此加班记录'
            })
            
        overtime = OvertimeService.update_overtime(overtime_id, data)
        return jsonify({
            'code': 200,
            'message': '更新加班记录成功',
            'data': overtime.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'更新加班记录失败: {str(e)}'
        })

@overtime_bp.route('/overtimes/<int:overtime_id>', methods=['DELETE'])
@login_required
def delete_overtime(overtime_id):
    """删除加班记录"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 401,
                'message': '未登录'
            })
            
        overtime = OvertimeService.get_overtime(overtime_id)
        
        if not overtime:
            return jsonify({
                'code': 404,
                'message': '加班记录不存在'
            })
            
        # 只允许本人或管理员删除
        if overtime.employee_id != user.employee.id and user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '无权删除此加班记录'
            })
            
        success = OvertimeService.delete_overtime(overtime_id)
        if success:
            return jsonify({
                'code': 200,
                'message': '删除加班记录成功'
            })
        return jsonify({
            'code': 500,
            'message': '删除加班记录失败'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'删除加班记录失败: {str(e)}'
        })

@overtime_bp.route('/overtimes/<int:overtime_id>/approve', methods=['POST'])
@login_required
def approve_overtime(overtime_id):
    """审批加班申请"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 401,
                'message': '未登录'
            })
            
        # 只允许管理员审批
        if user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '无权审批加班申请'
            })
            
        data = request.get_json()
        status = data.get('status', 'approved')  # 默认为approved
        
        overtime = OvertimeService.approve_overtime(overtime_id, user.id, status)
        if not overtime:
            return jsonify({
                'code': 404,
                'message': '加班记录不存在'
            })
            
        return jsonify({
            'code': 200,
            'message': '审批加班申请成功',
            'data': overtime.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'审批加班申请失败: {str(e)}'
        })
