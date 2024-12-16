from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# 导入所有模型
from .models.employee import Employee
from .models.department import Department
from .models.position import Position
from .models.attendance import Attendance, Leave, Overtime
from .models.salary import SalaryStructure, SalaryRecord

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 如果没有指定配置，使用开发环境配置
    if config_name is None:
        config_name = 'development'
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CONTRACTS_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 配置跨域
    CORS(app, resources={
        r"/*": {  # 允许所有路由
            "origins": ["http://localhost:3000"],  # 允许的源
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的方法
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],  # 允许的头部
            "supports_credentials": True  # 允许携带认证信息
        }
    })
    
    # 添加全局的 after_request 处理器
    @app.after_request
    def after_request(response):
        """全局响应处理器，添加必要的 CORS 头部"""
        # 允许的源
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:3000')
        # 允许的方法
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        # 允许的头部
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        # 允许携带认证信息
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        # 预检请求的有效期
        response.headers['Access-Control-Max-Age'] = '3600'
        # 如果是预检请求，设置状态码为 200
        if request.method == 'OPTIONS':
            response.status_code = 200
        return response

    # 配置静态文件路径
    app.static_folder = os.path.join(app.config['BASE_DIR'], 'static')
    app.static_url_path = '/static'

    # 确保上传目录存在
    uploads_dir = os.path.join(app.static_folder, 'uploads', 'photos')
    os.makedirs(uploads_dir, exist_ok=True)

    # 添加额外的静态文件路由用于上传文件访问
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        return send_from_directory(uploads_dir, filename)
    
    # 注册蓝图
    from .api.auth import bp as auth_bp
    from .api.employee import bp as employee_bp
    from .api.dashboard import bp as dashboard_bp
    from .api.department import bp as department_bp
    from .api.position import bp as position_bp
    from .api.salary import bp as salary_bp
    from .api.attendance import bp as attendance_bp
    from .api.user import bp as user_bp  # 导入新的用户蓝图
    from .api.intern import bp as intern_bp  # 导入实习管理蓝图
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(position_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(user_bp)  # 注册用户蓝图
    app.register_blueprint(intern_bp)  # 注册实习管理蓝图
    
    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/personnel_management.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Personnel Management startup')
    
    # 注册错误处理器
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'code': 400,
            'msg': '错误的请求'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'msg': '资源不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '服务器内部错误'
        }), 500
    
    return app
