from flask import Blueprint, request, jsonify
from app import db
from app.models import Employee, Attendance, AttendanceLocation, AttendanceRule, Department
from app.utils.auth import login_required
from datetime import datetime
from sqlalchemy import and_

attendance = Blueprint('attendance_api', __name__)

# ... (其他路由保持不变)

# 考勤规则相关路由
@attendance.route('/rules', methods=['GET'])
@login_required
def get_attendance_rules():
    """获取考勤规则列表
    
    Returns:
        JSON: 考勤规则列表数据
    """
    try:
        # 获取查询参数
        department_id = request.args.get('department_id', type=int)
        is_active = request.args.get('is_active', type=bool, default=True)
        
        # 构建查询
        query = AttendanceRule.query
        
        # 添加部门筛选
        if department_id:
            query = query.filter_by(department_id=department_id)
            
        # 添加生效状态筛选
        if is_active:
            current_date = datetime.now().date()
            query = query.filter(
                db.and_(
                    AttendanceRule.effective_start_date <= current_date,
                    db.or_(
                        AttendanceRule.effective_end_date >= current_date,
                        AttendanceRule.effective_end_date.is_(None)
                    )
                )
            )
            
        # 获取规则列表
        rules = query.order_by(AttendanceRule.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取考勤规则列表成功',
            'data': [rule.to_dict() for rule in rules]
        })
        
    except Exception as e:
        print(f"获取考勤规则列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取考勤规则列表失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules', methods=['POST'])
@login_required
def create_attendance_rule():
    """创建考勤规则
    
    Returns:
        JSON: 创建的考勤规则数据
    """
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['name', 'work_start_time', 'work_end_time', 'effective_start_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必要字段: {field}',
                    'data': None
                }), 400
                
        # 验证时间格式
        try:
            work_start_time = datetime.strptime(data['work_start_time'], '%H:%M').time()
            work_end_time = datetime.strptime(data['work_end_time'], '%H:%M').time()
            effective_start_date = datetime.strptime(data['effective_start_date'], '%Y-%m-%d').date()
            
            # 初始化 effective_end_date 为 None
            effective_end_date = None
            if 'effective_end_date' in data and data['effective_end_date']:
                effective_end_date = datetime.strptime(data['effective_end_date'], '%Y-%m-%d').date()
                if effective_end_date < effective_start_date:
                    return jsonify({
                        'code': 400,
                        'message': '结束日期不能早于开始日期',
                        'data': None
                    }), 400
        except ValueError as e:
            return jsonify({
                'code': 400,
                'message': f'日期格式错误: {str(e)}',
                'data': None
            }), 400
            
        # 验证规则类型
        rule_type = data.get('rule_type', 'regular')
        if rule_type not in ['regular', 'special', 'temporary']:
            return jsonify({
                'code': 400,
                'message': '无效的规则类型',
                'data': None
            }), 400
            
        # 检查是否存在冲突的规则
        department_id = data.get('department_id')
        if department_id:
            existing_rules = AttendanceRule.query.filter_by(department_id=department_id).all()
            new_rule = AttendanceRule(
                effective_start_date=effective_start_date,
                effective_end_date=effective_end_date,
                department_id=department_id
            )
            
            for rule in existing_rules:
                if rule.has_conflict_with(new_rule):
                    return jsonify({
                        'code': 400,
                        'message': f'与现有规则 {rule.name} 存在时间冲突',
                        'data': None
                    }), 400
            
        # 如果设置为默认规则，需要将其他规则的默认状态取消
        if data.get('is_default'):
            AttendanceRule.query.filter_by(is_default=True).update({'is_default': False})
            
        # 创建新规则
        new_rule = AttendanceRule(
            name=data['name'],
            work_start_time=work_start_time,
            work_end_time=work_end_time,
            late_threshold=data.get('late_threshold', 15),
            early_leave_threshold=data.get('early_leave_threshold', 15),
            overtime_minimum=data.get('overtime_minimum', 60),
            is_default=data.get('is_default', False),
            description=data.get('description', ''),
            department_id=department_id,
            effective_start_date=effective_start_date,
            effective_end_date=effective_end_date,
            flexible_time=data.get('flexible_time', 30),
            overtime_rate=data.get('overtime_rate', 1.5),
            weekend_overtime_rate=data.get('weekend_overtime_rate', 2.0),
            holiday_overtime_rate=data.get('holiday_overtime_rate', 3.0),
            priority=data.get('priority', 0),
            rule_type=rule_type
        )
        
        if 'break_start_time' in data and data['break_start_time']:
            new_rule.break_start_time = datetime.strptime(data['break_start_time'], '%H:%M').time()
        if 'break_end_time' in data and data['break_end_time']:
            new_rule.break_end_time = datetime.strptime(data['break_end_time'], '%H:%M').time()
            
        db.session.add(new_rule)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建考勤规则成功',
            'data': new_rule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"创建考勤规则失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'创建考勤规则失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>', methods=['PUT'])
@login_required
def update_attendance_rule(rule_id):
    """更新考勤规则
    
    Args:
        rule_id: 规则ID
        
    Returns:
        JSON: 更新后的考勤规则数据
    """
    try:
        # 获取规则对象
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        data = request.get_json()
        
        # 更新基本信息
        if 'name' in data:
            rule.name = data['name']
        if 'description' in data:
            rule.description = data['description']
            
        # 更新时间相关字段
        if 'work_start_time' in data:
            rule.work_start_time = datetime.strptime(data['work_start_time'], '%H:%M').time()
        if 'work_end_time' in data:
            rule.work_end_time = datetime.strptime(data['work_end_time'], '%H:%M').time()
        if 'break_start_time' in data:
            rule.break_start_time = datetime.strptime(data['break_start_time'], '%H:%M').time() if data['break_start_time'] else None
        if 'break_end_time' in data:
            rule.break_end_time = datetime.strptime(data['break_end_time'], '%H:%M').time() if data['break_end_time'] else None
            
        # 更新阈值设置
        if 'late_threshold' in data:
            rule.late_threshold = data['late_threshold']
        if 'early_leave_threshold' in data:
            rule.early_leave_threshold = data['early_leave_threshold']
        if 'overtime_minimum' in data:
            rule.overtime_minimum = data['overtime_minimum']
        if 'flexible_time' in data:
            rule.flexible_time = data['flexible_time']
            
        # 更新费率设置
        if 'overtime_rate' in data:
            rule.overtime_rate = data['overtime_rate']
        if 'weekend_overtime_rate' in data:
            rule.weekend_overtime_rate = data['weekend_overtime_rate']
        if 'holiday_overtime_rate' in data:
            rule.holiday_overtime_rate = data['holiday_overtime_rate']
            
        # 更新关联和状态
        if 'department_id' in data:
            rule.department_id = data['department_id']
        if 'is_default' in data:
            if data['is_default']:
                # 将其他规则的默认状态设为False
                AttendanceRule.query.filter(AttendanceRule.id != rule_id).update({'is_default': False})
            rule.is_default = data['is_default']
            
        # 更新生效日期
        if 'effective_start_date' in data:
            rule.effective_start_date = datetime.strptime(data['effective_start_date'], '%Y-%m-%d').date()
        if 'effective_end_date' in data:
            rule.effective_end_date = datetime.strptime(data['effective_end_date'], '%Y-%m-%d').date() if data['effective_end_date'] else None
            
        # 更新其他字段
        if 'priority' in data:
            rule.priority = data['priority']
        if 'rule_type' in data:
            rule.rule_type = data['rule_type']
            
        # 提交更改
        db.session.commit()
        
        # 刷新规则对象
        db.session.refresh(rule)
        
        return jsonify({
            'code': 200,
            'message': '更新考勤规则成功',
            'data': rule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"更新考勤规则失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新考勤规则失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>', methods=['DELETE'])
@login_required
def delete_attendance_rule(rule_id):
    """删除考勤规则
    
    Args:
        rule_id: 规则ID
        
    Returns:
        JSON: 删除结果
    """
    try:
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        # 不允许删除默认规则
        if rule.is_default:
            return jsonify({
                'code': 400,
                'message': '不能删除默认规则',
                'data': None
            }), 400
            
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除考勤规则成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除考勤规则失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>/assign/department', methods=['POST'])
@login_required
def assign_rule_to_department(rule_id):
    """将考勤规则分配给部门
    
    Args:
        rule_id: 规则ID
        
    Returns:
        JSON: 分配结果
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'department_ids' not in data:
            return jsonify({
                'code': 400,
                'message': '请求参数错误',
                'data': None
            }), 400
            
        department_ids = data['department_ids']
        if not isinstance(department_ids, list):
            return jsonify({
                'code': 400,
                'message': '部门ID必须是列表',
                'data': None
            }), 400
            
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        # 检查所有部门是否存在
        for department_id in department_ids:
            department = Department.query.get(department_id)
            if not department:
                return jsonify({
                    'code': 404,
                    'message': f'部门 {department_id} 不存在',
                    'data': None
                }), 404
                
        # 为每个部门分配规则
        try:
            for department_id in department_ids:
                # 设置部门ID
                rule.department_id = department_id
                
                # 获取部门下的所有员工
                employees = Employee.query.filter_by(department_id=department_id).all()
                
                # 更新每个员工的考勤规则
                for employee in employees:
                    if rule not in employee.attendance_rules:
                        employee.attendance_rules.append(rule)
                
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'message': '规则分配成功',
                'data': None
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"规则分配失败: {str(e)}")
            return jsonify({
                'code': 500,
                'message': f'数据库操作失败: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'规则分配失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>/assignments', methods=['GET'])
@login_required
def get_rule_assignments(rule_id):
    """获取考勤规则的分配信息
    
    Args:
        rule_id: 规则ID
        
    Returns:
        JSON: 规则的分配信息，包括部门和员工
    """
    try:
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        # 获取规则关联的部门信息
        departments = []
        if rule.department_id:
            department = Department.query.get(rule.department_id)
            if department:
                departments.append({
                    'id': department.id,
                    'name': department.name
                })
                
        # 获取直接分配给员工的信息（包括通过部门分配和直接分配的）
        assigned_employees = []
        # 通过部门分配的员工
        if rule.department_id:
            dept_employees = Employee.query.filter_by(department_id=rule.department_id).all()
            for emp in dept_employees:
                if emp not in assigned_employees:
                    assigned_employees.append(emp)
        
        # 直接分配的员工
        for emp in rule.employees:
            if emp not in assigned_employees:
                assigned_employees.append(emp)
        
        # 转换为响应格式
        employees = [{
            'id': emp.id,
            'name': emp.name,
            'department_name': emp.department.name if emp.department else None
        } for emp in assigned_employees]
        
        return jsonify({
            'code': 200,
            'message': '获取规则分配信息成功',
            'data': {
                'departments': departments,
                'employees': employees
            }
        })
        
    except Exception as e:
        print(f"获取规则分配信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取规则分配信息失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>/assignments/department/<int:department_id>', methods=['DELETE'])
@login_required
def unassign_rule_from_department(rule_id, department_id):
    """取消部门的考勤规则分配
    
    Args:
        rule_id: 规则ID
        department_id: 部门ID
        
    Returns:
        JSON: 操作结果
    """
    try:
        # 获取规则和部门对象
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'code': 404,
                'message': '部门不存在',
                'data': None
            }), 404
            
        # 检查规则是否分配给该部门
        if rule.department_id != department_id:
            return jsonify({
                'code': 400,
                'message': '该规则未分配给此部门',
                'data': None
            }), 400
            
        # 取消部门下所有员工的规则分配
        employees = Employee.query.filter_by(department_id=department_id).all()
        for employee in employees:
            if rule in employee.attendance_rules:
                employee.attendance_rules.remove(rule)
                
        # 取消部门分配
        rule.department_id = None
        
        # 提交更改并刷新对象
        db.session.commit()
        db.session.refresh(rule)
        
        return jsonify({
            'code': 200,
            'message': '取消部门规则分配成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"取消部门规则分配失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'取消部门规则分配失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>/assignments/employee/<int:employee_id>', methods=['DELETE'])
@login_required
def unassign_rule_from_employee(rule_id, employee_id):
    """取消员工的考勤规则分配
    
    Args:
        rule_id: 规则ID
        employee_id: 员工ID
        
    Returns:
        JSON: 操作结果
    """
    try:
        # 获取规则和员工对象
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在',
                'data': None
            }), 404
            
        # 检查规则是否已分配给员工
        if rule not in employee.attendance_rules:
            return jsonify({
                'code': 400,
                'message': '该规则未分配给此员工',
                'data': None
            }), 400
            
        # 从员工的规则列表中移除该规则
        employee.attendance_rules.remove(rule)
        
        # 提交更改并刷新对象
        db.session.commit()
        db.session.refresh(employee)
        
        return jsonify({
            'code': 200,
            'message': '取消员工规则分配成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"取消员工规则分配失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'取消员工规则分配失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/employee/<int:employee_id>', methods=['GET'])
@login_required
def get_employee_rules(employee_id):
    """获取员工的所有考勤规则，包括个人规则和部门规则
    
    Args:
        employee_id: 员工ID
        
    Returns:
        JSON: 员工的考勤规则列表
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在',
                'data': None
            }), 404
        
        # 获取员工的个人规则
        personal_rules = [rule.to_dict() for rule in employee.attendance_rules]
        
        # 获取部门规则
        department_rules = []
        if employee.department_id:
            dept_rules = AttendanceRule.query.filter_by(department_id=employee.department_id).all()
            department_rules = [rule.to_dict() for rule in dept_rules]
        
        return jsonify({
            'code': 200,
            'message': '获取员工考勤规则成功',
            'data': {
                'personal_rules': personal_rules,
                'department_rules': department_rules
            }
        })
        
    except Exception as e:
        print(f"获取员工考勤规则失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取员工考勤规则失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/employee/<int:employee_id>/active', methods=['GET'])
@login_required
def get_active_rule_for_employee(employee_id):
    """获取员工当前有效的考勤规则，优先返回个人规则，如果没有则返回部门规则
    
    Args:
        employee_id: 员工ID
        
    Returns:
        JSON: 员工当前有效的考勤规则
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在',
                'data': None
            }), 404
            
        check_date = request.args.get('date')
        if check_date:
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        else:
            check_date = datetime.now().date()
        
        # 首先查找员工的个人规则
        personal_rules = [rule for rule in employee.attendance_rules 
                         if rule.effective_start_date <= check_date and 
                         (rule.effective_end_date is None or rule.effective_end_date >= check_date)]
        
        # 如果有个人规则，返回优先级最高的
        if personal_rules:
            active_rule = max(personal_rules, key=lambda x: x.priority)
            return jsonify({
                'code': 200,
                'message': '获取员工当前有效考勤规则成功',
                'data': active_rule.to_dict()
            })
            
        # 如果没有个人规则，查找部门规则
        department_rule = AttendanceRule.query.filter(
            AttendanceRule.department_id == employee.department_id,
            AttendanceRule.effective_start_date <= check_date,
            db.or_(
                AttendanceRule.effective_end_date.is_(None),
                AttendanceRule.effective_end_date >= check_date
            )
        ).order_by(AttendanceRule.priority.desc()).first()
        
        if department_rule:
            return jsonify({
                'code': 200,
                'message': '获取员工当前有效考勤规则成功',
                'data': department_rule.to_dict()
            })
            
        return jsonify({
            'code': 404,
            'message': '未找到有效的考勤规则',
            'data': None
        }), 404
        
    except Exception as e:
        print(f"获取员工当前有效考勤规则失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取员工当前有效考勤规则失败: {str(e)}',
            'data': None
        }), 500

@attendance.route('/rules/<int:rule_id>/assign/employee', methods=['POST'])
@login_required
def assign_rule_to_employees(rule_id):
    """将考勤规则分配给员工
    
    Args:
        rule_id: 规则ID
        
    Returns:
        JSON: 分配结果
    """
    try:
        data = request.get_json()
        employee_ids = data.get('employee_ids', [])
        
        if not employee_ids:
            return jsonify({
                'code': 400,
                'message': '缺少员工ID列表',
                'data': None
            }), 400
            
        rule = AttendanceRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'code': 404,
                'message': '考勤规则不存在',
                'data': None
            }), 404
            
        # 开始事务
        try:
            for employee_id in employee_ids:
                employee = Employee.query.get(employee_id)
                if not employee:
                    return jsonify({
                        'code': 404,
                        'message': f'员工 {employee_id} 不存在',
                        'data': None
                    }), 404
                
                # 使用多对多关系添加规则，允许员工有多个规则
                if rule not in employee.attendance_rules:
                    employee.attendance_rules.append(rule)
            
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'message': '规则分配成功',
                'data': None
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"规则分配失败: {str(e)}")
            return jsonify({
                'code': 500,
                'message': f'数据库操作失败: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        print(f"规则分配失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'规则分配失败: {str(e)}',
            'data': None
        }), 500
