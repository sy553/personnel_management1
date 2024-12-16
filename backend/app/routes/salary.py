from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.auth import manager_required
from app.models import SalaryStructure, SalaryRecord, Employee
from app import db
from app.services.salary_service import SalaryService
from datetime import datetime

# 创建薪资管理蓝图
salary_bp = Blueprint('salary', __name__)

@salary_bp.route('/api/salary/structures', methods=['POST'])
@jwt_required()
@manager_required()
def create_salary_structure():
    """创建薪资结构"""
    try:
        data = request.get_json()

        # 验证必要字段
        required_fields = ['name', 'basic_salary', 'housing_allowance', 'transport_allowance', 'meal_allowance']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必要字段: {field}',
                    'data': None
                }), 400

        # 创建薪资结构
        salary_structure = SalaryStructure(
            name=data['name'],
            basic_salary=data['basic_salary'],
            housing_allowance=data['housing_allowance'],
            transport_allowance=data['transport_allowance'],
            meal_allowance=data['meal_allowance'],
            description=data.get('description')
        )

        db.session.add(salary_structure)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': salary_structure.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"创建薪资结构失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'创建失败: {str(e)}',
            'data': None
        }), 500

@salary_bp.route('/api/salary/structures', methods=['GET'])
@jwt_required()
def get_salary_structures():
    """获取薪资结构列表"""
    try:
        salary_structures = SalaryStructure.query.all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [structure.to_dict() for structure in salary_structures]
        })

    except Exception as e:
        print(f"获取薪资结构列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取薪资结构列表失败: {str(e)}',
            'data': None
        }), 500

@salary_bp.route('/api/salary/structures/<int:structure_id>', methods=['GET'])
@jwt_required()
def get_salary_structure(structure_id):
    """获取单个薪资结构"""
    try:
        salary_structure = SalaryStructure.query.get_or_404(structure_id)
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': salary_structure.to_dict()
        })

    except Exception as e:
        print(f"获取薪资结构失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取薪资结构失败: {str(e)}',
            'data': None
        }), 500

@salary_bp.route('/api/salary/structures/<int:structure_id>', methods=['PUT'])
@jwt_required()
@manager_required()
def update_salary_structure(structure_id):
    """更新薪资结构"""
    try:
        salary_structure = SalaryStructure.query.get_or_404(structure_id)
        data = request.get_json()

        # 更新字段
        if 'name' in data:
            salary_structure.name = data['name']
        if 'basic_salary' in data:
            salary_structure.basic_salary = data['basic_salary']
        if 'housing_allowance' in data:
            salary_structure.housing_allowance = data['housing_allowance']
        if 'transport_allowance' in data:
            salary_structure.transport_allowance = data['transport_allowance']
        if 'meal_allowance' in data:
            salary_structure.meal_allowance = data['meal_allowance']
        if 'description' in data:
            salary_structure.description = data['description']

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': salary_structure.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"更新薪资结构失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500

@salary_bp.route('/api/salary/structures/<int:structure_id>', methods=['DELETE'])
@jwt_required()
@manager_required()
def delete_salary_structure(structure_id):
    """删除薪资结构"""
    try:
        salary_structure = SalaryStructure.query.get_or_404(structure_id)
        db.session.delete(salary_structure)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })

    except Exception as e:
        db.session.rollback()
        print(f"删除薪资结构失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500

@salary_bp.route('/api/salary/records', methods=['GET'])
@jwt_required()
def get_salary_records():
    """
    获取工资记录列表和统计数据
    
    URL参数：
        year: 年份（可选，默认为当前年份）
        month: 月份（可选，默认为当前月份）
        department_id: 部门ID（可选）
        payment_status: 支付状态（可选）
    
    返回：
        {
            'code': 200,
            'message': '获取成功',
            'data': {
                'records': [...],  # 工资记录列表
                'statistics': {
                    'total_count': 本月记录数,
                    'paid_count': 已发放记录数,
                    'total_gross': 本月应发总额,
                    'total_net': 本月实发总额,
                    ...
                }
            }
        }
    """
    try:
        # 获取当前日期作为默认值
        current_date = datetime.now()
        
        # 获取查询参数，默认使用当前年月
        year = request.args.get('year', type=int) or current_date.year
        month = request.args.get('month', type=int) or current_date.month
        department_id = request.args.get('department_id', type=int)
        payment_status = request.args.get('payment_status')

        print(f"查询参数 - 年份: {year}, 月份: {month}, 部门ID: {department_id}, 支付状态: {payment_status}")

        # 构建基础查询
        base_query = SalaryRecord.query
        
        # 如果需要部门筛选，添加JOIN
        if department_id:
            base_query = base_query.join(Employee, SalaryRecord.employee_id == Employee.id)
            
        # 构建筛选条件
        conditions = [
            SalaryRecord.year == year,
            SalaryRecord.month == month
        ]
        
        # 添加部门筛选条件
        if department_id:
            conditions.append(Employee.department_id == department_id)
            
        # 添加支付状态筛选条件
        if payment_status:
            conditions.append(SalaryRecord.payment_status == payment_status)
            
        # 应用筛选条件
        base_query = base_query.filter(*conditions)
        
        # 获取记录列表
        records = base_query.all()
        print(f"找到 {len(records)} 条工资记录")
        
        # 按部门分组的统计数据
        department_statistics = {}
        
        # 如果指定了部门ID，只返回该部门的统计
        if department_id:
            statistics = {
                'total_count': len(records),
                'paid_count': sum(1 for r in records if r.payment_status == 'paid'),
                'total_basic': sum(float(r.basic_salary) for r in records),
                'total_allowances': sum(float(r.allowances) for r in records),
                'total_overtime': sum(float(r.overtime_pay) for r in records),
                'total_bonus': sum(float(r.bonus) for r in records),
                'total_tax': sum(float(r.tax) for r in records),
                'total_net': sum(float(r.net_salary) for r in records),
                'total_gross': sum(float(r.gross_salary) for r in records)
            }
        else:
            # 如果没有指定部门，按部门分组统计
            from itertools import groupby
            from operator import attrgetter
            
            # 先按部门ID排序
            sorted_records = sorted(records, key=lambda r: (r.employee.department_id if r.employee.department_id else 0))
            
            # 按部门分组统计
            for dept_id, dept_records in groupby(sorted_records, key=lambda r: r.employee.department_id):
                dept_records = list(dept_records)  # 转换为列表以便多次使用
                dept_name = dept_records[0].employee.department.name if dept_records[0].employee.department else "未分配部门"
                
                department_statistics[str(dept_id or 0)] = {
                    'department_name': dept_name,
                    'total_count': len(dept_records),
                    'paid_count': sum(1 for r in dept_records if r.payment_status == 'paid'),
                    'total_basic': sum(float(r.basic_salary) for r in dept_records),
                    'total_allowances': sum(float(r.allowances) for r in dept_records),
                    'total_overtime': sum(float(r.overtime_pay) for r in dept_records),
                    'total_bonus': sum(float(r.bonus) for r in dept_records),
                    'total_tax': sum(float(r.tax) for r in dept_records),
                    'total_net': sum(float(r.net_salary) for r in dept_records),
                    'total_gross': sum(float(r.gross_salary) for r in dept_records)
                }
            
            # 计算总体统计数据
            statistics = {
                'total_count': len(records),
                'paid_count': sum(1 for r in records if r.payment_status == 'paid'),
                'total_basic': sum(float(r.basic_salary) for r in records),
                'total_allowances': sum(float(r.allowances) for r in records),
                'total_overtime': sum(float(r.overtime_pay) for r in records),
                'total_bonus': sum(float(r.bonus) for r in records),
                'total_tax': sum(float(r.tax) for r in records),
                'total_net': sum(float(r.net_salary) for r in records),
                'total_gross': sum(float(r.gross_salary) for r in records)
            }
        
        print(f"统计数据: {statistics}")
        print(f"部门统计数据: {department_statistics}")

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'records': [record.to_dict() for record in records],
                'statistics': statistics,
                'department_statistics': department_statistics
            }
        })

    except Exception as e:
        print(f"获取工资记录失败: {str(e)}")
        db.session.rollback()  # 发生错误时回滚事务
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500
