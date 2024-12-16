from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.models import User

# 创建认证蓝图
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/send-reset-code', methods=['POST'])
def send_reset_code():
    """发送重置密码验证码接口"""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({
            "code": 400,
            "message": "请提供邮箱地址",
            "data": None
        }), 400
        
    # 调用发送验证码服务
    success, message = AuthService.send_reset_code(email=data['email'])
    
    if not success:
        return jsonify({
            "code": 400,
            "message": message,
            "data": None
        }), 400
        
    return jsonify({
        "code": 200,
        "message": message,
        "data": None
    })

@bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """验证重置密码验证码接口"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('code'):
        return jsonify({
            "code": 400,
            "message": "请提供邮箱和验证码",
            "data": None
        }), 400
        
    # 调用验证码验证服务
    success, message = AuthService.verify_reset_code(
        email=data['email'],
        code=data['code']
    )
    
    if not success:
        return jsonify({
            "code": 400,
            "message": message,
            "data": None
        }), 400
        
    return jsonify({
        "code": 200,
        "message": "验证码验证成功",
        "data": None
    })

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码接口"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['email', 'code', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必要字段: {field}",
                "data": None
            }), 400
            
    # 调用重置密码服务
    success, message = AuthService.reset_password_with_code(
        email=data['email'],
        code=data['code'],
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({
            "code": 400,
            "message": message,
            "data": None
        }), 400
        
    return jsonify({
        "code": 200,
        "message": "密码重置成功",
        "data": {}
    })

@bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['username', 'password', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必要字段: {field}",
                "data": None
            }), 400
            
    # 调用注册服务
    user, error = AuthService.register(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        role=data.get('role', 'employee')
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "data": None
        }), 400
        
    return jsonify({
        "code": 200,
        "message": "注册成功",
        "data": {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
    }), 201

@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """用户登录接口"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        response = jsonify({
            'code': 200,
            'message': 'success',
            'data': None
        })
        return response
        
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
        result, error = AuthService.login(
            username=data['username'],
            password=data['password']
        )
        
        if error:
            return jsonify({
                'code': 401,
                'message': error,
                'data': None
            }), 401
            
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': result['access_token'],
                'user': result['user']
            }
        })
    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({
        "code": 200,
        "message": "令牌刷新成功",
        "data": {
            "access_token": access_token
        }
    }), 200

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码接口"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必要字段
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({
            "code": 400,
            "message": "请提供旧密码和新密码",
            "data": None
        }), 400
        
    # 调用修改密码服务
    success, error = AuthService.change_password(
        user_id=current_user_id,
        old_password=data['old_password'],
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({
            "code": 400,
            "message": error,
            "data": None
        }), 400
        
    return jsonify({
        "code": 200,
        "message": "密码修改成功",
        "data": None
    }), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息接口"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "用户不存在",
            "data": None
        }), 404
        
    return jsonify({
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "user": user.to_dict()
        }
    }), 200
