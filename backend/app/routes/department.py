from flask import Blueprint, jsonify, request
from ..models.department import Department
from .. import db

# 创建蓝图
bp = Blueprint('department', __name__)

@bp.route('/departments', methods=['GET'])
def get_departments():
    """
    获取部门列表
    :return: 部门列表数据
    """
    try:
        # 查询所有部门
        departments = Department.query.all()
        
        # 转换为字典列表
        department_list = [dept.to_dict() for dept in departments]
        
        return jsonify({
            'code': 200,
            'message': '获取部门列表成功',
            'data': department_list
        })
    except Exception as e:
        print(f"获取部门列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取部门列表失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """
    获取指定部门信息
    :param department_id: 部门ID
    :return: 部门信息
    """
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'code': 404,
                'message': '部门不存在',
                'data': None
            }), 404
            
        return jsonify({
            'code': 200,
            'message': '获取部门信息成功',
            'data': department.to_dict()
        })
    except Exception as e:
        print(f"获取部门信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取部门信息失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/departments', methods=['POST'])
def create_department():
    """
    创建新部门
    :return: 新创建的部门信息
    """
    try:
        data = request.get_json()
        
        # 创建新部门
        department = Department(
            name=data.get('name'),
            description=data.get('description')
        )
        
        # 保存到数据库
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建部门成功',
            'data': department.to_dict()
        })
    except Exception as e:
        print(f"创建部门失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建部门失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/departments/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    """
    更新部门信息
    :param department_id: 部门ID
    :return: 更新后的部门信息
    """
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'code': 404,
                'message': '部门不存在',
                'data': None
            }), 404
            
        data = request.get_json()
        
        # 更新部门信息
        if 'name' in data:
            department.name = data['name']
        if 'description' in data:
            department.description = data['description']
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新部门信息成功',
            'data': department.to_dict()
        })
    except Exception as e:
        print(f"更新部门信息失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新部门信息失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/departments/<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    """
    删除部门
    :param department_id: 部门ID
    :return: 删除结果
    """
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'code': 404,
                'message': '部门不存在',
                'data': None
            }), 404
            
        # 删除部门
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除部门成功',
            'data': None
        })
    except Exception as e:
        print(f"删除部门失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除部门失败: {str(e)}',
            'data': None
        }), 500
