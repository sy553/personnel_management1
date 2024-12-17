"""
法定节假日管理API
"""
from flask import Blueprint, request, jsonify
from app.models.statutory_holiday import StatutoryHoliday
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

bp = Blueprint('statutory_holiday', __name__, url_prefix='/api/statutory-holidays')

@bp.route('', methods=['GET'])
def get_statutory_holidays():
    """获取法定节假日列表
    
    支持按年份和类型筛选
    """
    try:
        year = request.args.get('year', type=int)
        holiday_type = request.args.get('holiday_type')
        
        query = StatutoryHoliday.query
        
        if year:
            query = query.filter_by(year=year)
        if holiday_type:
            query = query.filter_by(holiday_type=holiday_type)
            
        holidays = query.order_by(StatutoryHoliday.date.asc()).all()
        return jsonify({
            'code': 200,
            'data': [holiday.to_dict() for holiday in holidays],
            'msg': '获取法定节假日列表成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取法定节假日列表失败: {str(e)}'
        })

@bp.route('', methods=['POST'])
@jwt_required()
def create_statutory_holiday():
    """创建法定节假日
    
    必填字段：name, date, holiday_type
    可选字段：description
    """
    try:
        # 检查用户权限
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({
                'code': 403,
                'msg': '只有管理员可以创建法定节假日'
            })
            
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['name', 'date', 'holiday_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
        
        # 解析日期
        try:
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'code': 400,
                'msg': '日期格式错误，应为YYYY-MM-DD'
            })
        
        # 验证节假日类型
        valid_types = ['holiday', 'workday']
        if data['holiday_type'] not in valid_types:
            return jsonify({
                'code': 400,
                'msg': f'节假日类型错误，应为: {", ".join(valid_types)}'
            })
        
        # 检查是否已存在
        existing = StatutoryHoliday.query.filter_by(date=date).first()
        if existing:
            return jsonify({
                'code': 400,
                'msg': f'该日期已存在节假日记录: {existing.name}'
            })
        
        # 创建节假日记录
        holiday = StatutoryHoliday(
            name=data['name'],
            date=date,
            holiday_type=data['holiday_type'],
            year=date.year,
            description=data.get('description')
        )
        
        db.session.add(holiday)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday.to_dict(),
            'msg': '创建法定节假日成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'创建法定节假日失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_statutory_holiday(id):
    """更新法定节假日"""
    try:
        # 检查用户权限
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({
                'code': 403,
                'msg': '只有管理员可以更新法定节假日'
            })
            
        holiday = StatutoryHoliday.query.get(id)
        if not holiday:
            return jsonify({
                'code': 404,
                'msg': '法定节假日不存在'
            })
        
        data = request.get_json()
        
        # 更新日期
        if 'date' in data:
            try:
                date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                # 检查新日期是否与其他记录冲突
                existing = StatutoryHoliday.query.filter(
                    StatutoryHoliday.date == date,
                    StatutoryHoliday.id != id
                ).first()
                if existing:
                    return jsonify({
                        'code': 400,
                        'msg': f'该日期已存在节假日记录: {existing.name}'
                    })
                holiday.date = date
                holiday.year = date.year
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '日期格式错误，应为YYYY-MM-DD'
                })
        
        # 更新节假日类型
        if 'holiday_type' in data:
            valid_types = ['holiday', 'workday']
            if data['holiday_type'] not in valid_types:
                return jsonify({
                    'code': 400,
                    'msg': f'节假日类型错误，应为: {", ".join(valid_types)}'
                })
            holiday.holiday_type = data['holiday_type']
        
        # 更新其他字段
        if 'name' in data:
            holiday.name = data['name']
        if 'description' in data:
            holiday.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': holiday.to_dict(),
            'msg': '更新法定节假日成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'更新法定节假日失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_statutory_holiday(id):
    """删除法定节假日"""
    try:
        # 检查用户权限
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({
                'code': 403,
                'msg': '只有管理员可以删除法定节假日'
            })
            
        holiday = StatutoryHoliday.query.get(id)
        if not holiday:
            return jsonify({
                'code': 404,
                'msg': '法定节假日不存在'
            })
        
        db.session.delete(holiday)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除法定节假日成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'删除法定节假日失败: {str(e)}'
        })
