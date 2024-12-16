from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app import db

# 创建用户蓝图
bp = Blueprint('user', __name__, url_prefix='/api/users')

@bp.route('/current', methods=['GET'])
@jwt_required()  # 需要JWT认证
def get_current_user():
    """获取当前登录用户信息"""
    try:
        # 从JWT中获取用户ID
        current_user_id = get_jwt_identity()
        
        # 查询用户信息
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在',
                'data': None
            }), 404
            
        # 返回用户信息
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
            }
        })
        
    except Exception as e:
        print(f"获取当前用户信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取用户信息失败: {str(e)}',
            'data': None
        }), 500
