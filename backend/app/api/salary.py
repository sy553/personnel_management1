from flask import Blueprint, request, jsonify
import logging
from app.models.salary import SalaryStructure, SalaryRecord
from app.models.salary_structure_assignment import SalaryStructureAssignment
from app.models.employee import Employee
from app.models.department import Department
from app import db
from datetime import datetime
from app.services.salary_service import SalaryService
from decimal import Decimal

# 创建蓝图，使用 url_prefix='/api'
bp = Blueprint('salary', __name__, url_prefix='/api')

# 创建蓝图，不设置 url_prefix，因为已经在前端固定了完整的 URL
# bp = Blueprint('salary', __name__)

@bp.route('/salary/structures', methods=['GET', 'POST', 'OPTIONS'])
def get_salary_structures():
    """获取工资结构列表"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if request.method == 'GET':
            structures = SalaryStructure.query.all()
            return jsonify({
                'code': 200,
                'data': [struct.to_dict() for struct in structures],
                'msg': '获取工资结构列表成功'
            })
        elif request.method == 'POST':
            data = request.get_json()
            
            # 验证必要字段
            required_fields = ['name', 'basic_salary']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'code': 400,
                        'msg': f'缺少必要字段: {field}'
                    })
            
            # 检查名称是否已存在
            existing_structure = SalaryStructure.query.filter_by(name=data['name']).first()
            if existing_structure:
                return jsonify({
                    'code': 400,
                    'msg': '该薪资结构名称已存在'
                })
                
            structure = SalaryStructure(
                name=data['name'],
                description=data.get('description', ''),
                basic_salary=data['basic_salary'],
                housing_allowance=data.get('housing_allowance', 0),
                transport_allowance=data.get('transport_allowance', 0),
                meal_allowance=data.get('meal_allowance', 0)
            )
            
            db.session.add(structure)
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'data': structure.to_dict(),
                'msg': '创建工资结构成功'
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'获取工资结构列表失败: {str(e)}'
        })

@bp.route('/salary/structures/<int:id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def get_salary_structure(id):
    """获取单个工资结构"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        structure = SalaryStructure.query.get(id)
        if not structure:
            return jsonify({
                'code': 404,
                'msg': '工资结构不存在'
            })
            
        if request.method == 'GET':
            return jsonify({
                'code': 200,
                'data': structure.to_dict(),
                'msg': '获取工资结构成功'
            })
        elif request.method == 'PUT':
            data = request.get_json()
            
            # 更新字段
            if 'name' in data:
                structure.name = data['name']
            if 'description' in data:
                structure.description = data['description']
            if 'basic_salary' in data:
                structure.basic_salary = data['basic_salary']
            if 'housing_allowance' in data:
                structure.housing_allowance = data['housing_allowance']
            if 'transport_allowance' in data:
                structure.transport_allowance = data['transport_allowance']
            if 'meal_allowance' in data:
                structure.meal_allowance = data['meal_allowance']
                
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'data': structure.to_dict(),
                'msg': '更新工资结构成功'
            })
        elif request.method == 'DELETE':
            try:
                # 检查是否有工资记录使用此结构（通过基本工资和其他字段匹配）
                records = SalaryRecord.query.filter(
                    SalaryRecord.basic_salary == structure.basic_salary,
                    SalaryRecord.allowances == (structure.housing_allowance + structure.transport_allowance + structure.meal_allowance)
                ).first()
                
                if records:
                    return jsonify({
                        'code': 400,
                        'msg': '该工资结构下可能存在工资记录，无法删除'
                    })
                    
                db.session.delete(structure)
                db.session.commit()
                
                return jsonify({
                    'code': 200,
                    'msg': '删除工资结构成功'
                })
            except Exception as e:
                db.session.rollback()
                print(f"删除工资结构时出错: {str(e)}")  # 添加日志记录
                return jsonify({
                    'code': 500,
                    'msg': f'删除工资结构失败: {str(e)}'
                })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'获取工资结构失败: {str(e)}'
        })

@bp.route('/salary/records', methods=['GET', 'POST', 'OPTIONS'])
def get_salary_records():
    """获取工资记录列表"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if request.method == 'GET':
            # 获取当前日期作为默认值
            current_date = datetime.now()
            
            # 获取查询参数，默认使用当前年月
            employee_id = request.args.get('employee_id', type=int)
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
            conditions = []
            
            # 添加基本筛选条件
            if employee_id:
                conditions.append(SalaryRecord.employee_id == employee_id)
            if year:
                conditions.append(SalaryRecord.year == year)
            if month:
                conditions.append(SalaryRecord.month == month)
            
            # 添加部门筛选条件
            if department_id:
                conditions.append(Employee.department_id == department_id)
            
            # 添加支付状态筛选条件
            if payment_status:
                conditions.append(SalaryRecord.payment_status == payment_status)
            
            # 应用所有筛选条件
            if conditions:
                base_query = base_query.filter(*conditions)
            
            # 获取记录列表
            records = base_query.all()
            print(f"找到 {len(records)} 条工资记录")
            
            # 计算统计数据
            total_count = len(records)
            paid_count = sum(1 for r in records if r.payment_status == 'paid')
            total_basic = sum(float(r.basic_salary) for r in records)
            total_allowances = sum(float(r.allowances) for r in records)
            total_overtime = sum(float(r.overtime_pay) for r in records)
            total_bonus = sum(float(r.bonus) for r in records)
            total_tax = sum(float(r.tax) for r in records)
            total_net = sum(float(r.net_salary) for r in records)
            total_gross = sum(float(r.gross_salary) for r in records)
            
            # 构建统计数据
            statistics = {
                'total': {  # 合计统计
                    'total_count': total_count,          # 本月记录数
                    'paid_count': paid_count,            # 已发放记录数
                    'total_basic': total_basic,          # 基本工资总额
                    'total_allowances': total_allowances,# 补贴总额
                    'total_overtime': total_overtime,    # 加班费总额
                    'total_bonus': total_bonus,          # 奖金总额
                    'total_tax': total_tax,              # 个税总额
                    'total_net': total_net,              # 本月实发总额
                    'total_gross': total_gross           # 本月应发总额
                },
                'pending': {  # 待发放统计
                    'total_count': sum(1 for r in records if r.payment_status == 'pending'),
                    'total_basic': sum(float(r.basic_salary) for r in records if r.payment_status == 'pending'),
                    'total_allowances': sum(float(r.allowances) for r in records if r.payment_status == 'pending'),
                    'total_overtime': sum(float(r.overtime_pay) for r in records if r.payment_status == 'pending'),
                    'total_bonus': sum(float(r.bonus) for r in records if r.payment_status == 'pending'),
                    'total_tax': sum(float(r.tax) for r in records if r.payment_status == 'pending'),
                    'total_net': sum(float(r.net_salary) for r in records if r.payment_status == 'pending'),
                    'total_gross': sum(float(r.gross_salary) for r in records if r.payment_status == 'pending')
                },
                'paid': {  # 已发放统计
                    'total_count': paid_count,
                    'total_basic': sum(float(r.basic_salary) for r in records if r.payment_status == 'paid'),
                    'total_allowances': sum(float(r.allowances) for r in records if r.payment_status == 'paid'),
                    'total_overtime': sum(float(r.overtime_pay) for r in records if r.payment_status == 'paid'),
                    'total_bonus': sum(float(r.bonus) for r in records if r.payment_status == 'paid'),
                    'total_tax': sum(float(r.tax) for r in records if r.payment_status == 'paid'),
                    'total_net': sum(float(r.net_salary) for r in records if r.payment_status == 'paid'),
                    'total_gross': sum(float(r.gross_salary) for r in records if r.payment_status == 'paid')
                }
            }
            
            print(f"统计数据: {statistics}")
            
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'records': [record.to_dict() for record in records],
                    'statistics': statistics
                }
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            
            # 验证必要字段
            required_fields = ['employee_id', 'year', 'month', 'basic_salary']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'code': 400,
                        'msg': f'缺少必要字段: {field}'
                    })
                    
            # 验证员工是否存在
            employee = Employee.query.get(data['employee_id'])
            if not employee:
                return jsonify({
                    'code': 404,
                    'msg': '员工不存在'
                })
                
            # 检查是否已有该月工资记录
            existing_record = SalaryRecord.query.filter_by(
                employee_id=data['employee_id'],
                year=data['year'],
                month=data['month']
            ).first()
            
            if existing_record:
                return jsonify({
                    'code': 400,
                    'msg': '该月已有工资记录'
                })
                
            # 创建新的工资记录
            record = SalaryRecord(
                employee_id=data['employee_id'],
                year=data['year'],
                month=data['month'],
                basic_salary=data['basic_salary'],
                allowances=data.get('allowances', 0),
                overtime_pay=data.get('overtime_pay', 0),
                bonus=data.get('bonus', 0),
                deductions=data.get('deductions', 0),
                tax=data.get('tax', 0),
                net_salary=data.get('net_salary', data['basic_salary']),  # 如果没有提供，默认等于基本工资
                payment_status=data.get('payment_status', 'pending'),
                payment_date=datetime.now() if data.get('payment_status') == 'paid' else None,
                remark=data.get('remark', '')
            )
            
            try:
                db.session.add(record)
                db.session.commit()
                return jsonify({
                    'code': 200,
                    'data': record.to_dict(),
                    'msg': '创建工资记录成功'
                })
            except Exception as e:
                db.session.rollback()
                print(f"创建工资记录时出错: {str(e)}")  # 添加日志记录
                return jsonify({
                    'code': 500,
                    'msg': f'创建工资记录失败: {str(e)}'
                })
                
    except Exception as e:
        print(f"处理工资记录请求时出错: {str(e)}")  # 添加日志记录
        return jsonify({
            'code': 500,
            'msg': f'处理工资记录请求失败: {str(e)}'
        })

@bp.route('/salary/records/<int:id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def get_salary_record(id):
    """获取单个工资记录"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        record = SalaryRecord.query.get(id)
        if not record:
            return jsonify({
                'code': 404,
                'msg': '工资记录不存在'
            })
            
        if request.method == 'GET':
            return jsonify({
                'code': 200,
                'data': record.to_dict(),
                'msg': '获取工资记录成功'
            })
        elif request.method == 'PUT':
            try:
                data = request.get_json()
                
                # 使用SalaryService更新工资记录
                updated_record = SalaryService.update_salary_record(
                    record_id=id,
                    data=data,
                    check_payment_status=True
                )
                
                return jsonify({
                    'code': 200,
                    'data': updated_record.to_dict(),
                    'msg': '更新工资记录成功'
                })
            except ValueError as e:
                return jsonify({
                    'code': 400,
                    'msg': str(e)
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'code': 500,
                    'msg': f'更新工资记录失败: {str(e)}'
                })
        elif request.method == 'DELETE':
            db.session.delete(record)
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'msg': '删除工资记录成功'
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'获取工资记录失败: {str(e)}'
        })

@bp.route('/salary/records/batch', methods=['POST'])
def batch_generate_salary_records():
    """
    批量生成工资记录的API端点
    
    请求体参数:
        year: 年份 (必需)
        month: 月份 (必需)
        employee_ids: 员工ID列表 (必需)
    
    返回:
        包含成功和失败记录的JSON响应
    """
    try:
        # 获取并验证请求参数
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '无效的请求数据',
                'data': None
            }), 400
        
        # 验证必需参数
        year = data.get('year')
        month = data.get('month')
        employee_ids = data.get('employee_ids')
        
        if not year or not month:
            return jsonify({
                'code': 400,
                'message': '年份和月份是必需的参数',
                'data': None
            }), 400
            
        if not employee_ids:
            return jsonify({
                'code': 400,
                'message': '请指定要生成工资记录的员工',
                'data': None
            }), 400
        
        try:
            year = int(year)
            month = int(month)
        except (TypeError, ValueError):
            return jsonify({
                'code': 400,
                'message': '年份和月份必须是有效的整数',
                'data': None
            }), 400
        
        # 验证年月的有效性
        if not (1900 <= year <= 9999):
            return jsonify({
                'code': 400,
                'message': '年份必须在1900到9999之间',
                'data': None
            }), 400
            
        if not (1 <= month <= 12):
            return jsonify({
                'code': 400,
                'message': '月份必须在1到12之间',
                'data': None
            }), 400
        
        # 验证员工ID列表
        if not isinstance(employee_ids, list):
            return jsonify({
                'code': 400,
                'message': 'employee_ids必须是一个列表',
                'data': None
            }), 400
            
        try:
            employee_ids = [int(id) for id in employee_ids]
        except (TypeError, ValueError):
            return jsonify({
                'code': 400,
                'message': 'employee_ids列表中的所有ID必须是有效的整数',
                'data': None
            }), 400
        
        # 调用服务层方法生成工资记录
        result = SalaryService.batch_generate_salary_records(
            year=year,
            month=month,
            employee_ids=employee_ids
        )
        
        # 根据结果构造响应
        success_count = len(result.get('success', []))
        failed_count = len(result.get('failed', []))
        
        if success_count == 0 and failed_count > 0:
            # 如果全部失败，返回400状态码
            return jsonify({
                'code': 400,
                'message': f'工资记录生成失败，共{failed_count}条失败记录',
                'data': result
            }), 400
        elif success_count > 0 and failed_count > 0:
            # 如果部分成功部分失败，返回207状态码
            return jsonify({
                'code': 207,
                'message': f'工资记录生成部分成功: {success_count}条成功, {failed_count}条失败',
                'data': result
            }), 207
        else:
            # 如果全部成功，返回200状态码
            return jsonify({
                'code': 200,
                'message': f'工资记录生成完成: {success_count}条成功',
                'data': result
            }), 200
            
    except Exception as e:
        import logging
        logging.error(f"批量生成工资记录时发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500

@bp.route('/salary/statistics', methods=['GET', 'OPTIONS'])
def get_salary_statistics():
    """获取薪资统计数据"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 获取查询参数
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 获取统计数据
        statistics = SalaryService.get_salary_statistics(
            year,
            month,
            department_id
        )
        
        return jsonify({
            'code': 200,
            'data': statistics,
            'msg': '获取薪资统计数据成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取薪资统计数据失败: {str(e)}'
        })

@bp.route('/salary/records/<int:id>/send-slip', methods=['POST', 'OPTIONS'])
def send_salary_slip(id):
    """发送工资条"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 发送工资条
        success = SalaryService.send_salary_slip(id)
        
        if success:
            return jsonify({
                'code': 200,
                'msg': '工资条发送成功'
            })
        else:
            return jsonify({
                'code': 500,
                'msg': '工资条发送失败'
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'工资条发送失败: {str(e)}'
        })

@bp.route('/salary/records/batch-send-slips', methods=['POST', 'OPTIONS'])
def batch_send_salary_slips():
    """批量发送工资条"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['year', 'month']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
        
        # 获取可选的员工ID列表
        employee_ids = data.get('employee_ids')
        
        # 批量发送工资条
        result = SalaryService.batch_send_salary_slips(
            data['year'],
            data['month'],
            employee_ids
        )
        
        return jsonify({
            'code': 200,
            'data': {
                'success_count': len(result['success']),
                'failed_count': len(result['failed']),
                'failed_employees': result['failed']
            },
            'msg': '批量发送工资条完成'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'批量发送工资条失败: {str(e)}'
        })

@bp.route('/salary/calculate-tax', methods=['POST', 'OPTIONS'])
def calculate_tax():
    """计算个人所得税"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'gross_salary' not in data:
            return jsonify({
                'code': 400,
                'msg': '缺少必要字段: gross_salary'
            })
        
        # 计算个税
        tax = SalaryService.calculate_tax(Decimal(str(data['gross_salary'])))
        
        return jsonify({
            'code': 200,
            'data': {
                'tax': float(tax)
            },
            'msg': '计算个税成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'计算个税失败: {str(e)}'
        })

@bp.route('/salary/calculate-net', methods=['POST', 'OPTIONS'])
def calculate_net_salary():
    """计算实发工资"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'basic_salary' not in data:
            return jsonify({
                'code': 400,
                'msg': '缺少必要字段: basic_salary'
            })
        
        # 计算实发工资
        result = SalaryService.calculate_net_salary(
            Decimal(str(data['basic_salary'])),
            Decimal(str(data.get('allowances', 0))),
            Decimal(str(data.get('overtime_pay', 0))),
            Decimal(str(data.get('bonus', 0))),
            Decimal(str(data.get('deductions', 0)))
        )
        
        return jsonify({
            'code': 200,
            'data': {
                'gross_salary': float(result['gross_salary']),
                'tax': float(result['tax']),
                'net_salary': float(result['net_salary'])
            },
            'msg': '计算实发工资成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'计算实发工资失败: {str(e)}'
        })

@bp.route('/salary/personal', methods=['GET', 'OPTIONS'])
def get_personal_salary_records():
    """获取个人工资记录"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 从请求参数中获取查询条件
        employee_id = request.args.get('employee_id', type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not employee_id:
            return jsonify({
                'code': 400,
                'msg': '缺少员工ID参数'
            })
            
        # 构建查询条件
        query = SalaryRecord.query.filter_by(employee_id=employee_id)
        
        if year:
            query = query.filter_by(year=year)
        if month:
            query = query.filter_by(month=month)
            
        # 获取工资记录
        records = query.order_by(
            SalaryRecord.year.desc(),
            SalaryRecord.month.desc()
        ).all()
        
        # 获取员工信息
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'code': 404,
                'msg': '员工不存在'
            })
            
        # 计算统计数据
        total_records = len(records)
        total_net_salary = sum(record.net_salary for record in records)
        average_salary = total_net_salary / total_records if total_records > 0 else 0
        
        return jsonify({
            'code': 200,
            'data': {
                'employee': employee.to_dict(),
                'records': [record.to_dict() for record in records],
                'statistics': {
                    'total_records': total_records,
                    'total_net_salary': float(total_net_salary),
                    'average_salary': float(average_salary)
                }
            },
            'msg': '获取个人工资记录成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取个人工资记录失败: {str(e)}'
        })

@bp.route('/salary/structures/assign', methods=['POST', 'OPTIONS'])
def assign_salary_structure():
    """为员工或部门分配薪资结构"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['salary_structure_id', 'effective_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'缺少必要字段: {field}'
                })
        
        # 获取要分配的工资结构
        salary_structure = SalaryStructure.query.get(data['salary_structure_id'])
        if not salary_structure:
            return jsonify({
                'code': 404,
                'msg': '工资结构不存在'
            })
            
        # 解析日期字段
        effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d').date()
        expiry_date = None
        if 'expiry_date' in data and data['expiry_date']:
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            # 确保失效日期在生效日期之后
            if expiry_date <= effective_date:
                return jsonify({
                    'code': 400,
                    'msg': '失效日期必须在生效日期之后'
                })
                
        # 如果指定了员工ID，为员工分配工资结构
        if 'employee_id' in data:
            employee = Employee.query.get(data['employee_id'])
            if not employee:
                return jsonify({
                    'code': 404,
                    'msg': '员工不存在'
                })
            
            # 创建员工的工资结构分配记录
            structure_assignment = SalaryStructureAssignment(
                salary_structure_id=salary_structure.id,
                employee_id=employee.id,
                department_id=None,  # 员工专属分配时，department_id必须为空
                is_default=False,  # 员工专属工资结构
                effective_date=effective_date,
                expiry_date=expiry_date,
                is_active=data.get('is_active', True)  # 默认为激活状态
            )
            db.session.add(structure_assignment)
                
        # 如果指定了部门ID，为部门创建默认工资结构
        elif 'department_id' in data:
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({
                    'code': 404,
                    'msg': '部门不存在'
                })
                
            # 创建部门的默认工资结构分配记录
            structure_assignment = SalaryStructureAssignment(
                salary_structure_id=salary_structure.id,
                employee_id=None,  # 部门默认分配时，employee_id必须为空
                department_id=department.id,
                is_default=True,  # 部门默认工资结构
                effective_date=effective_date,
                expiry_date=expiry_date,
                is_active=data.get('is_active', True)  # 默认为激活状态
            )
            db.session.add(structure_assignment)
        
        # 如果是全局默认工资结构
        elif data.get('is_default'):
            # 创建全局默认工资结构分配记录
            structure_assignment = SalaryStructureAssignment(
                salary_structure_id=salary_structure.id,
                employee_id=None,  # 全局默认分配时，employee_id必须为空
                department_id=None,  # 全局默认分配时，department_id必须为空
                is_default=True,
                effective_date=effective_date,
                expiry_date=expiry_date,
                is_active=data.get('is_active', True)  # 默认为激活状态
            )
            db.session.add(structure_assignment)
        
        try:
            db.session.commit()
            return jsonify({
                'code': 200,
                'msg': '工资结构分配成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'code': 500,
                'msg': f'工资结构分配失败: {str(e)}'
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'工资结构分配失败: {str(e)}'
        })

@bp.route('/salary/structure-assignments', methods=['GET', 'OPTIONS'])
def get_salary_structure_assignments():
    """获取工资结构分配记录列表"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 获取查询参数
        employee_id = request.args.get('employee_id', type=int)
        department_id = request.args.get('department_id', type=int)
        is_default = request.args.get('is_default', type=bool)
        is_active = request.args.get('is_active', type=bool)
        date = request.args.get('date')  # 用于筛选在指定日期有效的分配记录
        
        # 构建查询
        query = SalaryStructureAssignment.query
        
        # 根据参数过滤
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if department_id:
            # 获取部门下所有员工的ID
            employees = Employee.query.filter_by(department_id=department_id).all()
            employee_ids = [emp.id for emp in employees]
            query = query.filter(SalaryStructureAssignment.employee_id.in_(employee_ids))
        if is_default is not None:
            query = query.filter_by(is_default=is_default)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
            
        # 如果指定了日期，筛选在该日期有效的分配记录
        if date:
            query_date = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(
                SalaryStructureAssignment.effective_date <= query_date,
                or_(
                    SalaryStructureAssignment.expiry_date.is_(None),
                    SalaryStructureAssignment.expiry_date > query_date
                )
            )
            
        # 按生效日期倒序排序
        assignments = query.order_by(SalaryStructureAssignment.effective_date.desc()).all()
        
        return jsonify({
            'code': 200,
            'data': [assignment.to_dict() for assignment in assignments],
            'msg': '获取工资结构分配记录成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取工资结构分配记录失败: {str(e)}'
        })

@bp.route('/salary/structure-assignments/<int:id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def manage_salary_structure_assignment(id):
    """管理工资结构分配记录"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        assignment = SalaryStructureAssignment.query.get(id)
        if not assignment:
            return jsonify({
                'code': 404,
                'msg': '工资结构分配记录不存在'
            })
            
        if request.method == 'GET':
            return jsonify({
                'code': 200,
                'data': assignment.to_dict(),
                'msg': '获取工资结构分配记录成功'
            })
        elif request.method == 'PUT':
            data = request.get_json()
            
            # 允许修改的字段
            if 'effective_date' in data:
                effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d').date()
                # 如果有失效日期，确保生效日期在失效日期之前
                if assignment.expiry_date and effective_date >= assignment.expiry_date:
                    return jsonify({
                        'code': 400,
                        'msg': '生效日期必须在失效日期之前'
                    })
                assignment.effective_date = effective_date
                
            if 'expiry_date' in data:
                if data['expiry_date']:
                    expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
                    # 确保失效日期在生效日期之后
                    if expiry_date <= assignment.effective_date:
                        return jsonify({
                            'code': 400,
                            'msg': '失效日期必须在生效日期之后'
                        })
                    assignment.expiry_date = expiry_date
                else:
                    assignment.expiry_date = None
                    
            if 'is_active' in data:
                assignment.is_active = data['is_active']
                
            db.session.commit()
            return jsonify({
                'code': 200,
                'data': assignment.to_dict(),
                'msg': '更新工资结构分配记录成功'
            })
        elif request.method == 'DELETE':
            db.session.delete(assignment)
            db.session.commit()
            return jsonify({
                'code': 200,
                'msg': '删除工资结构分配记录成功'
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'管理工资结构分配记录失败: {str(e)}'
        })

@bp.route('/salary/records/batch', methods=['PUT', 'DELETE', 'OPTIONS'])
def batch_manage_salary_records():
    """批量管理工资记录"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        record_ids = data.get('record_ids', [])
        
        if not record_ids:
            return jsonify({
                'code': 400,
                'msg': '未提供工资记录ID'
            })
            
        if request.method == 'PUT':
            # 批量更新
            update_data = data.get('data', {})
            check_payment_status = data.get('check_payment_status', True)
            
            results = SalaryService.batch_update_salary_records(
                record_ids=record_ids,
                data=update_data,
                check_payment_status=check_payment_status
            )
            
            return jsonify({
                'code': 200,
                'data': results,
                'msg': '批量更新工资记录完成'
            })
            
        elif request.method == 'DELETE':
            # 批量删除
            check_payment_status = data.get('check_payment_status', True)
            
            results = SalaryService.batch_delete_salary_records(
                record_ids=record_ids,
                check_payment_status=check_payment_status
            )
            
            return jsonify({
                'code': 200,
                'data': results,
                'msg': '批量删除工资记录完成'
            })
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'批量操作工资记录失败: {str(e)}'
        })
