from flask import jsonify, current_app
from flask import Blueprint
from app.models.employee import Employee
from app.models.department import Department
from app.models.position import Position
from app import db

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        # 获取各种统计数据
        total_employees = Employee.query.count()
        total_departments = Department.query.count()
        total_positions = Position.query.count()
        
        # 获取最近添加的员工
        recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
        recent_employees_data = [{
            'id': emp.id,
            'name': emp.name,
            'department': emp.department.name if emp.department else '未分配',
            'position': emp.position.name if emp.position else '未分配',
            'created_at': emp.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for emp in recent_employees]

        # 部门员工数量统计
        department_stats = db.session.query(
            Department.name,
            db.func.count(Employee.id).label('count')
        ).outerjoin(Employee, Department.id == Employee.department_id)\
         .group_by(Department.id, Department.name).all()
        
        department_stats_data = [{
            'name': dept[0],
            'count': dept[1]
        } for dept in department_stats]

        return jsonify({
            'overview': {
                'total_employees': total_employees,
                'total_departments': total_departments,
                'total_positions': total_positions
            },
            'recent_employees': recent_employees_data,
            'department_stats': department_stats_data
        })

    except Exception as e:
        error_message = f"Error getting dashboard stats: {str(e)}"
        current_app.logger.error(error_message)
        return jsonify({
            'message': '获取统计数据失败',
            'error': error_message,
            'error_details': str(e)
        }), 500
