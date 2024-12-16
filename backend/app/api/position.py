from flask import Blueprint, request, jsonify
from app.models.position import Position
from app import db

bp = Blueprint('position', __name__, url_prefix='/api')

@bp.route('/positions', methods=['GET'])
def get_positions():
    """获取职位列表"""
    try:
        positions = Position.query.all()
        return jsonify({
            'code': 200,
            'data': [pos.to_dict() for pos in positions],
            'msg': '获取职位列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取职位列表失败: {str(e)}'
        })

@bp.route('/positions/<int:id>', methods=['GET'])
def get_position(id):
    """获取单个职位信息"""
    try:
        position = Position.query.get(id)
        if not position:
            return jsonify({
                'code': 404,
                'msg': '职位不存在'
            })
        return jsonify({
            'code': 200,
            'data': position.to_dict(),
            'msg': '获取职位信息成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取职位信息失败: {str(e)}'
        })

@bp.route('/positions', methods=['POST'])
def create_position():
    """创建新职位"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'msg': '职位名称不能为空'
            })
            
        # 检查职位名称是否已存在
        existing_position = Position.query.filter_by(name=data['name']).first()
        if existing_position:
            return jsonify({
                'code': 400,
                'msg': '该职位名称已存在'
            })
            
        position = Position(
            name=data['name'],
            description=data.get('description', ''),
            department_id=data.get('department_id'),
            level=data.get('level', 1)
        )
        
        db.session.add(position)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': position.to_dict(),
            'msg': '创建职位成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建职位失败: {str(e)}'
        })

@bp.route('/positions/<int:id>', methods=['PUT'])
def update_position(id):
    """更新职位信息"""
    try:
        position = Position.query.get(id)
        if not position:
            return jsonify({
                'code': 404,
                'msg': '职位不存在'
            })
            
        data = request.get_json()
        
        # 如果要更新名称，检查是否与其他职位重复
        if 'name' in data and data['name'] != position.name:
            existing_position = Position.query.filter_by(name=data['name']).first()
            if existing_position:
                return jsonify({
                    'code': 400,
                    'msg': '该职位名称已存在'
                })
            position.name = data['name']
            
        if 'description' in data:
            position.description = data['description']
        if 'department_id' in data:
            position.department_id = data['department_id']
        if 'level' in data:
            position.level = data['level']
        if 'status' in data:
            position.status = data['status']
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': position.to_dict(),
            'msg': '更新职位成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'更新职位失败: {str(e)}'
        })

@bp.route('/positions/<int:id>', methods=['DELETE'])
def delete_position(id):
    """删除职位"""
    try:
        position = Position.query.get(id)
        if not position:
            return jsonify({
                'code': 404,
                'msg': '职位不存在'
            })
            
        # 检查是否有员工在该职位
        if position.employees.count() > 0:
            return jsonify({
                'code': 400,
                'msg': '该职位下有员工，无法删除'
            })
            
        db.session.delete(position)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除职位成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'删除职位失败: {str(e)}'
        })
