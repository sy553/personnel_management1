from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import auth, employee, upload, dashboard, department, position  # 导入所有API模块
