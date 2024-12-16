"""
实习管理API接口
"""

from flask import Blueprint, request, jsonify, current_app
from app.models.employee import Employee
from app.models.intern_status import InternStatus, InternEvaluation
from app.models.department import Department
from app.models.position import Position
from app import db
from datetime import datetime
from sqlalchemy import and_, or_
from flask_jwt_extended import jwt_required

bp = Blueprint('intern', __name__, url_prefix='/api/intern')

@bp.route('/status', methods=['GET'])
@jwt_required()
def get_intern_status_list():
    """获取实习状态列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status')
        keyword = request.args.get('keyword')
        
        # 构建查询
        query = InternStatus.query
        
        # 部门筛选
        if department_id:
            query = query.filter_by(department_id=department_id)
            
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
            
        # 关键词搜索
        if keyword:
            query = query.join(Employee, InternStatus.employee_id == Employee.id).filter(
                or_(
                    Employee.name.ilike(f'%{keyword}%'),
                    Employee.employee_id.ilike(f'%{keyword}%')
                )
            )
            
        # 分页
        pagination = query.order_by(InternStatus.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'msg': '获取实习状态列表成功',
            'data': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'items': [status.to_dict() for status in pagination.items]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取实习状态列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'获取实习状态列表失败: {str(e)}'
        })

@bp.route('/status/<int:id>', methods=['GET'])
@jwt_required()
def get_intern_status(id):
    """获取实习状态详情"""
    try:
        status = InternStatus.query.get(id)
        if not status:
            return jsonify({
                'code': 404,
                'msg': '实习状态记录不存在'
            })
            
        return jsonify({
            'code': 200,
            'data': status.to_dict(),
            'msg': '获取实习状态成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取实习状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'获取实习状态失败: {str(e)}'
        })

@bp.route('/status', methods=['POST'])
@jwt_required()
def create_intern_status():
    """创建实习状态记录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['employee_id', 'start_date', 'planned_end_date', 'department_id', 'position_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必填字段: {field}'
                })
                
        # 检查员工是否存在
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({
                'code': 404,
                'msg': '员工不存在'
            })
            
        # 检查是否已有进行中的实习记录
        existing_status = InternStatus.query.filter(
            and_(
                InternStatus.employee_id == data['employee_id'],
                InternStatus.status.in_(['intern', 'probation'])
            )
        ).first()
        
        if existing_status:
            return jsonify({
                'code': 400,
                'msg': '该员工已有进行中的实习或试用记录'
            })
            
        # 创建实习状态记录
        status = InternStatus(
            employee_id=data['employee_id'],
            status='intern',
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            planned_end_date=datetime.strptime(data['planned_end_date'], '%Y-%m-%d').date(),
            mentor_id=data.get('mentor_id'),
            department_id=data['department_id'],
            position_id=data['position_id'],
            comments=data.get('comments')
        )
        
        db.session.add(status)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': status.to_dict(),
            'msg': '创建实习状态记录成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建实习状态记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'创建实习状态记录失败: {str(e)}'
        })

@bp.route('/status/<int:id>', methods=['PUT'])
@jwt_required()
def update_intern_status(id):
    """更新实习状态记录"""
    try:
        status = InternStatus.query.get(id)
        if not status:
            return jsonify({
                'code': 404,
                'msg': '实习状态记录不存在'
            })
            
        data = request.get_json()
        
        # 更新字段
        for key, value in data.items():
            if key in ['start_date', 'planned_end_date', 'actual_end_date'] and value:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            setattr(status, key, value)
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': status.to_dict(),
            'msg': '更新实习状态记录成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新实习状态记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'更新实习状态记录失败: {str(e)}'
        })

@bp.route('/evaluations', methods=['POST'])
@jwt_required()
def create_evaluation():
    """创建实习评估"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = [
            'intern_status_id', 'evaluation_date', 'evaluation_type',
            'work_performance', 'learning_ability', 'communication_skill',
            'professional_skill', 'attendance', 'evaluator_id'
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必填字段: {field}'
                })
                
        # 检查实习状态是否存在
        status = InternStatus.query.get(data['intern_status_id'])
        if not status:
            return jsonify({
                'code': 404,
                'msg': '实习状态记录不存在'
            })
            
        # 计算总分
        total_score = sum([
            data['work_performance'],
            data['learning_ability'],
            data['communication_skill'],
            data['professional_skill'],
            data['attendance']
        ])
        
        # 创建评估记录
        evaluation = InternEvaluation(
            intern_status_id=data['intern_status_id'],
            evaluation_date=datetime.strptime(data['evaluation_date'], '%Y-%m-%d').date(),
            evaluation_type=data['evaluation_type'],
            work_performance=data['work_performance'],
            learning_ability=data['learning_ability'],
            communication_skill=data['communication_skill'],
            professional_skill=data['professional_skill'],
            attendance=data['attendance'],
            total_score=total_score,
            evaluation_content=data.get('evaluation_content'),
            improvement_suggestions=data.get('improvement_suggestions'),
            conversion_recommended=data.get('conversion_recommended', False),
            recommended_position_id=data.get('recommended_position_id'),
            recommended_salary=data.get('recommended_salary'),
            conversion_comments=data.get('conversion_comments'),
            evaluator_id=data['evaluator_id']
        )
        
        db.session.add(evaluation)
        
        # 如果是转正评估，且推荐转正，更新实习状态
        if data['evaluation_type'] == 'final' and data.get('conversion_recommended'):
            status.status = 'probation'  # 更新为试用期
            status.actual_end_date = datetime.strptime(data['evaluation_date'], '%Y-%m-%d').date()
            
            if data.get('recommended_position_id'):
                status.position_id = data['recommended_position_id']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': evaluation.to_dict(),
            'msg': '创建实习评估成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建实习评估失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'创建实习评估失败: {str(e)}'
        })

@bp.route('/evaluations/<int:id>', methods=['GET'])
@jwt_required()
def get_evaluation(id):
    """获取评估详情"""
    try:
        evaluation = InternEvaluation.query.get(id)
        if not evaluation:
            return jsonify({
                'code': 404,
                'msg': '评估记录不存在'
            })
            
        return jsonify({
            'code': 200,
            'data': evaluation.to_dict(),
            'msg': '获取评估记录成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取评估记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'获取评估记录失败: {str(e)}'
        })

@bp.route('/status/<int:status_id>/evaluations', methods=['GET'])
@jwt_required()
def get_status_evaluations(status_id):
    """获取实习状态的所有评估"""
    try:
        evaluations = InternEvaluation.query.filter_by(
            intern_status_id=status_id
        ).order_by(InternEvaluation.evaluation_date.desc()).all()
        
        return jsonify({
            'code': 200,
            'data': [evaluation.to_dict() for evaluation in evaluations],
            'msg': '获取评估记录列表成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取评估记录列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'获取评估记录列表失败: {str(e)}'
        })
