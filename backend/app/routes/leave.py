from flask import Blueprint, request, jsonify
from app.services.leave_service import LeaveService
from app.utils.auth import login_required
from flask_jwt_extended import get_jwt_identity
from app.models import User

# 创建蓝图
leave_bp = Blueprint('leave', __name__)

@leave_bp.route('/leaves', methods=['GET'])
@login_required
def get_leaves():
    """获取请假记录列表"""
    try:
        # 获取查询参数
        employee_id = request.args.get('employee_id', type=int)
        status = request.args.get('status')
        
        # 获取请假记录
        leaves = LeaveService.get_leaves(employee_id, status)
        return jsonify({
            'code': 200,
            'message': '获取请假记录成功',
            'data': [leave.to_dict() for leave in leaves]
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取请假记录失败: {str(e)}'
        })

@leave_bp.route('/leaves/<int:leave_id>', methods=['GET'])
@login_required
def get_leave(leave_id):
    """获取单个请假记录"""
    try:
        leave = LeaveService.get_leave(leave_id)
        if not leave:
            return jsonify({
                'code': 404,
                'message': '请假记录不存在'
            })
        return jsonify({
            'code': 200,
            'message': '获取请假记录成功',
            'data': leave.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取请假记录失败: {str(e)}'
        })

@leave_bp.route('/leaves', methods=['POST'])
@login_required
def create_leave():
    """创建请假记录"""
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
        leave = LeaveService.create_leave(data)
        return jsonify({
            'code': 200,
            'message': '创建请假记录成功',
            'data': leave.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'创建请假记录失败: {str(e)}'
        })

@leave_bp.route('/leaves/<int:leave_id>', methods=['PUT'])
@login_required
def update_leave(leave_id):
    """更新请假记录"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 401,
                'message': '未登录'
            })
            
        data = request.get_json()
        leave = LeaveService.get_leave(leave_id)
        
        if not leave:
            return jsonify({
                'code': 404,
                'message': '请假记录不存在'
            })
            
        # 只允许本人或管理员修改
        if leave.employee_id != user.employee.id and user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '无权修改此请假记录'
            })
            
        leave = LeaveService.update_leave(leave_id, data)
        return jsonify({
            'code': 200,
            'message': '更新请假记录成功',
            'data': leave.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'更新请假记录失败: {str(e)}'
        })

@leave_bp.route('/leaves/<int:leave_id>', methods=['DELETE'])
@login_required
def delete_leave(leave_id):
    """删除请假记录"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 401,
                'message': '未登录'
            })
            
        leave = LeaveService.get_leave(leave_id)
        
        if not leave:
            return jsonify({
                'code': 404,
                'message': '请假记录不存在'
            })
            
        # 只允许本人或管理员删除
        if leave.employee_id != user.employee.id and user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '无权删除此请假记录'
            })
            
        success = LeaveService.delete_leave(leave_id)
        if success:
            return jsonify({
                'code': 200,
                'message': '删除请假记录成功'
            })
        return jsonify({
            'code': 500,
            'message': '删除请假记录失败'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'删除请假记录失败: {str(e)}'
        })

@leave_bp.route('/leaves/<int:leave_id>/approve', methods=['POST'])
@login_required
def approve_leave(leave_id):
    """审批请假申请"""
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
                'message': '无权审批请假申请'
            })
            
        data = request.get_json()
        status = data.get('status', 'approved')  # 默认为approved
        
        leave = LeaveService.approve_leave(leave_id, user.id, status)
        if not leave:
            return jsonify({
                'code': 404,
                'message': '请假记录不存在'
            })
            
        return jsonify({
            'code': 200,
            'message': '审批请假申请成功',
            'data': leave.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'审批请假申请失败: {str(e)}'
        })
