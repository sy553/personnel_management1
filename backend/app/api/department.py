from flask import Blueprint, request, jsonify
from app.models.department import Department
from app import db

bp = Blueprint('department', __name__, url_prefix='/api')

@bp.route('/departments', methods=['GET'])
def get_departments():
    """获取部门列表"""
    try:
        departments = Department.query.all()
        return jsonify({
            'code': 200,
            'data': [dept.to_dict() for dept in departments],
            'msg': '获取部门列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取部门列表失败: {str(e)}'
        })

@bp.route('/departments/<int:id>', methods=['GET'])
def get_department(id):
    """获取单个部门信息"""
    try:
        department = Department.query.get(id)
        if not department:
            return jsonify({
                'code': 404,
                'msg': '部门不存在'
            })
        return jsonify({
            'code': 200,
            'data': department.to_dict(),
            'msg': '获取部门信息成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取部门信息失败: {str(e)}'
        })

@bp.route('/departments', methods=['POST'])
def create_department():
    """创建新部门"""
    try:
        data = request.get_json()
        
        # 检查必要字段
        if 'name' not in data:
            return jsonify({
                'code': 400,
                'msg': '部门名称不能为空'
            })
            
        department = Department(
            name=data['name'],
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            manager_id=data.get('manager_id'),
            level=data.get('level', 1)
        )
        
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': department.to_dict(),
            'msg': '创建部门成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建部门失败: {str(e)}'
        })

@bp.route('/departments/<int:id>', methods=['PUT'])
def update_department(id):
    """更新部门信息"""
    try:
        department = Department.query.get(id)
        if not department:
            return jsonify({
                'code': 404,
                'msg': '部门不存在'
            })
            
        data = request.get_json()
        if 'name' in data:
            department.name = data['name']
        if 'description' in data:
            department.description = data['description']
        if 'parent_id' in data:
            department.parent_id = data['parent_id']
        if 'manager_id' in data:
            department.manager_id = data['manager_id']
        if 'level' in data:
            department.level = data['level']
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': department.to_dict(),
            'msg': '更新部门成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'更新部门失败: {str(e)}'
        })

@bp.route('/departments/<int:id>', methods=['DELETE'])
def delete_department(id):
    """删除部门"""
    try:
        department = Department.query.get(id)
        if not department:
            return jsonify({
                'code': 404,
                'msg': '部门不存在'
            })
            
        # 检查是否有子部门
        if department.children.count() > 0:
            return jsonify({
                'code': 400,
                'msg': '该部门下有子部门，无法删除'
            })
            
        # 检查是否有员工
        if department.employees.count() > 0:
            return jsonify({
                'code': 400,
                'msg': '该部门下有员工，无法删除'
            })
            
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除部门成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'删除部门失败: {str(e)}'
        })
