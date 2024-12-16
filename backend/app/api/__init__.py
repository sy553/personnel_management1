from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import auth, employee, upload, dashboard, department, position, intern  # 导入所有API模块

def init_app(app):
    app.register_blueprint(auth.bp)
    app.register_blueprint(employee.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(department.bp)
    app.register_blueprint(position.bp)
    app.register_blueprint(intern.bp)  # 注册实习管理蓝图
