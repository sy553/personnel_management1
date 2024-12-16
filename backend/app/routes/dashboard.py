from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Employee, Department, Position

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取仪表盘统计数据"""
    try:
        # 获取员工总数
        total_employees = Employee.query.count()
        
        # 获取部门总数
        total_departments = Department.query.count()
        
        # 获取职位总数
        total_positions = Position.query.count()
        
        # 获取各部门员工数量分布
        department_stats = []
        departments = Department.query.all()
        for dept in departments:
            employee_count = Employee.query.filter_by(department_id=dept.id).count()
            department_stats.append({
                'name': dept.name,
                'value': employee_count
            })
            
        # 获取各职位员工数量分布
        position_stats = []
        positions = Position.query.all()
        for pos in positions:
            employee_count = Employee.query.filter_by(position_id=pos.id).count()
            position_stats.append({
                'name': pos.name,
                'value': employee_count
            })
        
        return jsonify({
            'code': 200,
            'message': '获取统计数据成功',
            'data': {
                'totalEmployees': total_employees,
                'totalDepartments': total_departments,
                'totalPositions': total_positions,
                'departmentStats': department_stats,
                'positionStats': position_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取统计数据失败: {str(e)}',
            'data': None
        }), 500
