from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.models import User, Employee

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['username', 'password', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"缺少必要字段: {field}"}), 400
            
    # 调用注册服务
    user, error = AuthService.register(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        role=data.get('role', 'employee')
    )
    
    if error:
        return jsonify({"msg": error}), 400
        
    return jsonify({
        "msg": "注册成功",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'code': 400,
                'message': '请提供用户名和密码',
                'data': None
            }), 400
            
        # 验证用户名和密码
        user, error = AuthService.authenticate(
            username=data['username'],
            password=data['password']
        )
        
        if error:
            return jsonify({
                'code': 401,
                'message': error,
                'data': None
            }), 401
            
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        
        # 获取员工信息
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        # 构建用户信息
        user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        
        # 如果存在员工信息，添加到返回数据中
        if employee:
            user_info.update({
                'employeeId': employee.id,
                'employeeName': employee.name,
                'departmentId': employee.department_id,
                'positionId': employee.position_id
            })
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': access_token,
                'user': user_info
            }
        })
    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}',
            'data': None
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": access_token}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码接口"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必要字段
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({"msg": "请提供旧密码和新密码"}), 400
        
    # 调用修改密码服务
    success, error = AuthService.change_password(
        user_id=current_user_id,
        old_password=data['old_password'],
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({"msg": error}), 400
        
    return jsonify({"msg": "密码修改成功"}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码接口"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({"msg": "请提供邮箱地址"}), 400
        
    # 调用重置密码服务
    success, message = AuthService.reset_password(email=data['email'])
    
    if not success:
        return jsonify({"msg": message}), 400
        
    return jsonify({"msg": message}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息接口"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "用户不存在"}), 404
        
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }), 200
