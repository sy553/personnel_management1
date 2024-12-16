from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User

def admin_required():
    """管理员权限装饰器"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role != 'admin':
                return jsonify({"msg": "需要管理员权限"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def manager_required():
    """管理者权限装饰器"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role not in ['admin', 'manager']:
                return jsonify({"msg": "需要管理者权限"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
