"""
薪资服务模块
提供薪资计算、发放和统计相关的业务逻辑
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
from sqlalchemy import and_, func, or_, case
from app import db
from app.models.salary import SalaryStructure, SalaryRecord
from app.models.salary_structure_assignment import SalaryStructureAssignment
from app.models.employee import Employee
from app.services.email_service import EmailService
from app.utils.pdf_generator import generate_pdf

class SalaryService:
    @staticmethod
    def calculate_tax(gross_salary: Decimal) -> Decimal:
        """
        计算个人所得税
        使用最新的个税计算方法（2024年）
        
        参数：
            gross_salary: 税前工资总额
            
        返回：
            计算得出的个人所得税金额
        """
        # 起征点
        tax_threshold = Decimal('5000')
        
        # 如果不超过起征点，无需缴税
        if gross_salary <= tax_threshold:
            return Decimal('0')
        
        # 应纳税所得额
        taxable_income = gross_salary - tax_threshold
        
        # 税率表
        tax_rates = [
            (0, 3000, 0.03, 0),
            (3000, 12000, 0.1, 210),
            (12000, 25000, 0.2, 1410),
            (25000, 35000, 0.25, 2660),
            (35000, 55000, 0.3, 4410),
            (55000, 80000, 0.35, 7160),
            (80000, float('inf'), 0.45, 15160)
        ]
        
        # 计算税额
        for low, high, rate, quick_deduction in tax_rates:
            if low < taxable_income <= high:
                tax = taxable_income * Decimal(str(rate)) - Decimal(str(quick_deduction))
                return tax.quantize(Decimal('0.01'))
                
        return Decimal('0')

    @staticmethod
    def calculate_overtime_pay(base_salary: Decimal, hours: int, rate: float = 1.5) -> Decimal:
        """
        计算加班费
        
        参数：
            base_salary: 基本工资
            hours: 加班小时数
            rate: 加班费率，默认1.5倍
            
        返回：
            计算得出的加班费金额
        """
        # 计算时薪（按照21.75天，每天8小时计算）
        hourly_rate = base_salary / Decimal('21.75') / Decimal('8')
        overtime_pay = hourly_rate * Decimal(str(hours)) * Decimal(str(rate))
        return overtime_pay.quantize(Decimal('0.01'))

    @staticmethod
    def calculate_net_salary(
        basic_salary: Decimal,
        allowances: Decimal = Decimal('0'),
        overtime_pay: Decimal = Decimal('0'),
        bonus: Decimal = Decimal('0'),
        deductions: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        计算实发工资
        
        计算步骤：
        1. 计算应发总额（税前）= 基本工资 + 补贴 + 加班费 + 奖金
        2. 计算个人所得税
        3. 计算实发工资 = 应发总额 - 个税 - 其他扣除项
        
        参数：
            basic_salary: 基本工资
            allowances: 补贴总额（包括住房补贴、交通补贴、餐饮补贴等）
            overtime_pay: 加班费
            bonus: 奖金
            deductions: 其他扣除项（如请假扣款等）
            
        返回：
            包含以下字段的字典：
            - gross_salary: 应发总额（税前）
            - tax: 个人所得税
            - net_salary: 实发工资
        """
        try:
            # 1. 计算应发总额（税前）
            gross_salary = (
                basic_salary +    # 基本工资
                allowances +      # 各项补贴
                overtime_pay +    # 加班费
                bonus            # 奖金
            ).quantize(Decimal('0.01'))  # 保留两位小数
            
            # 2. 计算个人所得税
            tax = SalaryService.calculate_tax(gross_salary).quantize(Decimal('0.01'))
            
            # 3. 计算实发工资 = 应发总额 - 个税 - 其他扣除项
            net_salary = (gross_salary - tax - deductions).quantize(Decimal('0.01'))
            
            # 返回计算结果
            return {
                'gross_salary': gross_salary,  # 应发总额
                'tax': tax,                    # 个人所得税
                'net_salary': net_salary       # 实发工资
            }
            
        except Exception as e:
            print(f"计算工资时出错: {str(e)}")
            raise ValueError(f"计算工资时出错: {str(e)}")

    @staticmethod
    def get_salary_structure_assignment(employee_id: int, date: datetime) -> Optional[SalaryStructureAssignment]:
        """
        获取指定日期的工资结构分配
        
        按以下优先级获取：
        1. 员工专属工资结构（如果存在且在有效期内）
        2. 部门工资结构（如果员工属于某个部门且工资结构在有效期内）
        3. 全局默认工资结构（如果在有效期内）
        
        参数：
            employee_id: 员工ID
            date: 指定日期
            
        返回：
            工资结构分配对象，如果没有找到则返回None
        """
        print(f"正在查找员工ID:{employee_id}在{date}的工资结构分配...")
        
        # 获取员工信息
        employee = Employee.query.get(employee_id)
        if not employee:
            print(f"未找到员工(ID:{employee_id})")
            return None
            
        print(f"尝试查找专属工资结构...")
        # 1. 查找员工专属的工资结构分配
        assignment = SalaryStructureAssignment.query.filter(
            SalaryStructureAssignment.employee_id == employee_id,
            SalaryStructureAssignment.is_active == True,
            SalaryStructureAssignment.effective_date <= date,
            (
                (SalaryStructureAssignment.expiry_date.is_(None)) |  # 无过期日期
                (SalaryStructureAssignment.expiry_date >= date)      # 或未过期
            )
        ).first()
        
        if assignment:
            print(f"找到专属工资结构: {assignment.salary_structure.name}")
            return assignment
            
        # 2. 查找部门的工资结构分配（不再检查is_default）
        if employee.department:
            print(f"尝试查找部门{employee.department.name}的工资结构...")
            assignment = SalaryStructureAssignment.query.filter(
                SalaryStructureAssignment.department_id == employee.department.id,
                SalaryStructureAssignment.is_active == True,
                SalaryStructureAssignment.effective_date <= date,
                (
                    (SalaryStructureAssignment.expiry_date.is_(None)) |  # 无过期日期
                    (SalaryStructureAssignment.expiry_date >= date)      # 或未过期
                )
            ).first()
            
            if assignment:
                print(f"找到部门{employee.department.name}的工资结构: {assignment.salary_structure.name}")
                return assignment
            print(f"未找到部门{employee.department.name}的工资结构")
        
        # 3. 查找全局默认的工资结构分配
        print("尝试查找全局默认的工资结构...")
        assignment = SalaryStructureAssignment.query.filter(
            SalaryStructureAssignment.employee_id.is_(None),  # 无指定员工
            SalaryStructureAssignment.department_id.is_(None),  # 无指定部门
            SalaryStructureAssignment.is_default == True,  # 必须是默认工资结构
            SalaryStructureAssignment.is_active == True,
            SalaryStructureAssignment.effective_date <= date,
            (
                (SalaryStructureAssignment.expiry_date.is_(None)) |  # 无过期日期
                (SalaryStructureAssignment.expiry_date >= date)      # 或未过期
            )
        ).first()
        
        if assignment:
            print(f"找到全局默认工资结构: {assignment.salary_structure.name}")
            return assignment
            
        print("未找到有效的工资结构分配")
        return None

    @staticmethod
    def generate_salary_record(
        employee_id: int,
        year: int,
        month: int,
        overtime_hours: int = 0,
        bonus: Decimal = Decimal('0'),
        deductions: Decimal = Decimal('0'),
        remark: str = '',
        force_update: bool = False,
        check_date: datetime = None  # 新增参数，用于指定检查工资结构的日期
    ) -> Optional[SalaryRecord]:
        """
        生成工资记录
        
        参数：
            employee_id: 员工ID
            year: 年份
            month: 月份
            overtime_hours: 加班小时数
            bonus: 奖金
            deductions: 扣除项
            remark: 备注
            force_update: 是否强制更新已存在的记录
            check_date: 指定检查工资结构的日期，默认为工资月份的1号
            
        返回：
            生成的工资记录对象，如果生成失败则返回None
        """
        try:
            # 获取员工信息
            employee = Employee.query.get(employee_id)
            if not employee:
                raise ValueError(f'员工不存在(ID:{employee_id})')

            # 检查是否已存在该月工资记录
            existing_record = SalaryRecord.query.filter_by(
                employee_id=employee_id,
                year=year,
                month=month
            ).first()
            
            # 如果记录已存在且不是强制更新，则抛出异常
            if existing_record and not force_update:
                raise ValueError(f'员工(ID:{employee_id})在{year}年{month}月已有工资记录')
            
            # 获取指定日期的工资结构分配
            check_date = check_date or datetime(year, month, 1)
            salary_assignment = SalaryService.get_salary_structure_assignment(employee_id, check_date)
            
            if not salary_assignment:
                raise ValueError(f'未找到员工(ID:{employee_id})在{check_date.date()}的有效工资结构分配')
            
            # 获取工资结构
            salary_structure = salary_assignment.salary_structure
            
            # 计算加班费
            overtime_pay = SalaryService.calculate_overtime_pay(
                salary_structure.basic_salary,
                overtime_hours
            )
            
            # 计算补贴总额
            allowances = (
                salary_structure.housing_allowance +
                salary_structure.transport_allowance +
                salary_structure.meal_allowance
            )
            
            # 计算总应发金额和实发工资
            salary_calc = SalaryService.calculate_net_salary(
                salary_structure.basic_salary,  # 基本工资
                allowances,                     # 补贴总额
                overtime_pay,                   # 加班费
                bonus,                         # 奖金
                deductions                     # 扣除项
            )
            
            # 获取计算结果
            gross_salary = salary_calc['gross_salary']  # 总应发金额
            tax = salary_calc['tax']                    # 个人所得税
            net_salary = salary_calc['net_salary']      # 实发工资
            
            # 准备工资结构信息的备注
            structure_info = (
                f"\n[工资结构信息]\n"
                f"名称: {salary_structure.name}\n"
                f"基本工资: {salary_structure.basic_salary}\n"
                f"住房补贴: {salary_structure.housing_allowance}\n"
                f"交通补贴: {salary_structure.transport_allowance}\n"
                f"餐饮补贴: {salary_structure.meal_allowance}\n"
                f"生效日期: {salary_structure.effective_date}\n"
                f"\n[工资计算明细]\n"
                f"基本工资: {salary_structure.basic_salary}\n"
                f"补贴总额: {allowances}\n"
                f"加班费: {overtime_pay}\n"
                f"奖金: {bonus}\n"
                f"应发总额: {gross_salary}\n"
                f"个人所得税: {tax}\n"
                f"其他扣除项: {deductions}\n"
                f"实发工资: {net_salary}\n"
            )
            
            # 如果是更新已存在的记录
            if existing_record and force_update:
                existing_record.basic_salary = salary_structure.basic_salary
                existing_record.allowances = allowances
                existing_record.overtime_pay = overtime_pay
                existing_record.bonus = bonus
                existing_record.deductions = deductions
                existing_record.gross_salary = gross_salary  # 添加总应发金额
                existing_record.tax = tax
                existing_record.net_salary = net_salary
                # 在备注中添加更新信息和工资结构信息
                update_info = f'{remark}\n[更新于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
                existing_record.remark = update_info + structure_info
                return existing_record
            
            # 创建新的工资记录
            record = SalaryRecord(
                employee_id=employee_id,
                year=year,
                month=month,
                basic_salary=salary_structure.basic_salary,
                allowances=allowances,
                overtime_pay=overtime_pay,
                bonus=bonus,
                deductions=deductions,
                gross_salary=gross_salary,  # 添加总应发金额
                tax=tax,
                net_salary=net_salary,
                payment_status='pending',  # 设置初始状态为待发放
                remark=remark + structure_info  # 在备注中添加工资结构信息
            )
            
            db.session.add(record)
            return record
            
        except Exception as e:
            print(f'生成工资记录时出错: {str(e)}')
            raise e

    @staticmethod
    def batch_generate_salary_records(
        year: int,
        month: int,
        employee_ids: List[int] = None
    ) -> Dict[str, List]:
        """
        批量生成工资记录
        
        参数：
            year: 年份
            month: 月份
            employee_ids: 员工ID列表，必须指定要生成工资记录的员工
            
        返回：
            包含成功和失败记录的字典
        """
        success_records = []
        failed_records = []
        
        # 设置检查工资结构的日期为目标月份的1号
        check_date = datetime(year, month, 1)
        
        # 获取员工列表
        query = Employee.query.filter(Employee.employment_status == 'active')
        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
        employees = query.all()
        
        if not employees:
            return {
                'success': [],
                'failed': [],
                'message': '未找到有效的员工记录'
            }
            
        # 批量处理每个员工
        for employee in employees:
            try:
                print(f"正在查找员工{employee.name}(ID:{employee.id})在{check_date.strftime('%Y-%m-%d')}的工资结构分配...")
                
                # 检查是否已存在工资记录
                existing_record = SalaryRecord.query.filter_by(
                    employee_id=employee.id,
                    year=year,
                    month=month
                ).first()
                
                if existing_record:
                    failed_records.append({
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'department': employee.department.name if employee.department else '未分配',
                        'error': '该月工资记录已存在'
                    })
                    continue
                    
                # 获取工资结构分配
                salary_assignment = SalaryService.get_salary_structure_assignment(employee.id, check_date)
                if not salary_assignment:
                    failed_records.append({
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'department': employee.department.name if employee.department else '未分配',
                        'error': '未找到有效的工资结构分配'
                    })
                    continue
                    
                # 计算补贴总额
                total_allowances = (
                    salary_assignment.salary_structure.housing_allowance +
                    salary_assignment.salary_structure.transport_allowance +
                    salary_assignment.salary_structure.meal_allowance
                )
                
                # 生成工资记录
                record = SalaryRecord(
                    employee_id=employee.id,
                    year=year,
                    month=month,
                    basic_salary=salary_assignment.salary_structure.basic_salary,
                    allowances=total_allowances,
                    overtime_pay=Decimal('0'),
                    bonus=Decimal('0'),
                    deductions=Decimal('0'),
                    payment_status='pending'
                )
                
                # 计算工资详情
                salary_calc = SalaryService.calculate_net_salary(
                    record.basic_salary,
                    record.allowances,
                    record.overtime_pay,
                    record.bonus,
                    record.deductions
                )
                
                # 更新所有金额字段
                record.gross_salary = salary_calc['gross_salary']  # 更新总应发金额
                record.tax = salary_calc['tax']
                record.net_salary = salary_calc['net_salary']
                
                # 添加工资结构信息到备注
                record.remark = (
                    f"[工资结构信息]\n"
                    f"名称: {salary_assignment.salary_structure.name}\n"
                    f"基本工资: {salary_assignment.salary_structure.basic_salary:.2f}\n"
                    f"住房补贴: {salary_assignment.salary_structure.housing_allowance:.2f}\n"
                    f"交通补贴: {salary_assignment.salary_structure.transport_allowance:.2f}\n"
                    f"餐饮补贴: {salary_assignment.salary_structure.meal_allowance:.2f}\n"
                    f"生效日期: {salary_assignment.salary_structure.effective_date}\n"
                )
                
                # 保存记录
                db.session.add(record)
                db.session.commit()
                
                success_records.append({
                    'employee_id': employee.id,
                    'employee_name': employee.name,
                    'department': employee.department.name if employee.department else '未分配',
                    'record_id': record.id,
                    'salary_structure': salary_assignment.salary_structure.name,
                    'basic_salary': float(record.basic_salary),
                    'allowances': float(record.allowances),
                    'tax': float(record.tax),
                    'net_salary': float(record.net_salary)
                })
                
            except Exception as e:
                db.session.rollback()
                failed_records.append({
                    'employee_id': employee.id,
                    'employee_name': employee.name,
                    'department': employee.department.name if employee.department else '未分配',
                    'error': str(e)
                })
                continue
                
        # 返回处理结果，包含详细的汇总信息
        result = {
            'success': success_records,
            'failed': failed_records
        }
        
        # 添加汇总信息
        if not success_records and failed_records:
            result['error'] = '所有工资记录生成失败，请检查工资结构分配'
        elif success_records and failed_records:
            result['message'] = f'部分工资记录生成成功：{len(success_records)}条成功，{len(failed_records)}条失败'
        else:
            result['message'] = f'所有工资记录生成成功：{len(success_records)}条'
            
        return result

    @staticmethod
    def batch_update_salary_records(
        year: int,
        month: int,
        employee_ids: List[int] = None
    ) -> Dict[str, List]:
        """
        批量更新工资记录
        
        参数：
            year: 年份
            month: 月份
            employee_ids: 员工ID列表，如果为None则更新所有员工
            
        返回：
            包含更新成功和失败记录的字典
        """
        success_records = []
        failed_records = []
        
        try:
            print(f'开始批量更新{year}年{month}月的工资记录...')
            
            # 验证是否提供了员工ID列表
            if not employee_ids:
                print('未指定要更新工资记录的员工')
                return {
                    'success': [],
                    'failed': [{
                        'employee_id': None,
                        'employee_name': None,
                        'department_name': None,
                        'reason': '请指定要更新工资记录的员工'
                    }]
                }
            
            # 获取指定的员工信息
            print(f'查询指定的{len(employee_ids)}名员工...')
            employees = Employee.query.filter(
                Employee.id.in_(employee_ids)
            ).all()
            
            if not employees:
                print('未找到指定的员工')
                return {
                    'success': [],
                    'failed': [{
                        'employee_id': None,
                        'employee_name': None,
                        'department_name': None,
                        'reason': '未找到指定的员工'
                    }]
                }
            
            print(f'找到{len(employees)}名员工')
            
            # 检查每个员工的工资结构分配情况
            check_date = datetime(year, month, 1)
            for emp in employees:
                try:
                    print(f'\n处理员工{emp.name}(ID:{emp.id})的工资记录...')
                    
                    # 检查是否已存在工资记录
                    existing_record = SalaryRecord.query.filter_by(
                        employee_id=emp.id,
                        year=year,
                        month=month
                    ).first()
                    
                    if existing_record:
                        print(f'员工{emp.name}已存在{year}年{month}月的工资记录')
                        failed_records.append({
                            'employee_id': emp.id,
                            'employee_name': emp.name,
                            'department_name': emp.department.name if emp.department else '未分配',
                            'reason': '已存在工资记录'
                        })
                        continue
                    
                    # 检查员工工资结构分配
                    salary_structure = SalaryService.get_salary_structure_assignment(emp.id, check_date)
                    if not salary_structure:
                        print(f'员工{emp.name}没有有效的工资结构分配')
                        failed_records.append({
                            'employee_id': emp.id,
                            'employee_name': emp.name,
                            'department_name': emp.department.name if emp.department else '未分配',
                            'reason': f'未找到{year}年{month}月的有效工资结构分配'
                        })
                        continue
                    
                    # 生成工资记录
                    print(f'开始生成员工{emp.name}的工资记录...')
                    record = SalaryRecord(
                        employee_id=emp.id,
                        year=year,
                        month=month,
                        basic_salary=salary_structure.salary_structure.basic_salary,
                        allowances=(
                            salary_structure.salary_structure.housing_allowance +
                            salary_structure.salary_structure.transport_allowance +
                            salary_structure.salary_structure.meal_allowance
                        ),
                        overtime_pay=Decimal('0'),
                        bonus=Decimal('0'),
                        deductions=Decimal('0'),
                        payment_status='pending'
                    )
                    
                    # 计算税收和实发工资
                    salary_calc = SalaryService.calculate_net_salary(
                        record.basic_salary,
                        record.allowances,
                        record.overtime_pay,
                        record.bonus,
                        record.deductions
                    )
                    record.tax = salary_calc['tax']
                    record.net_salary = salary_calc['net_salary']
                    record.gross_salary = salary_calc['gross_salary']  # 添加总应发金额
                    
                    # 添加工资结构信息到备注
                    record.remark = (
                        f"[工资结构信息]\n"
                        f"名称: {salary_structure.salary_structure.name}\n"
                        f"基本工资: {salary_structure.salary_structure.basic_salary:.2f}\n"
                        f"住房补贴: {salary_structure.salary_structure.housing_allowance:.2f}\n"
                        f"交通补贴: {salary_structure.salary_structure.transport_allowance:.2f}\n"
                        f"餐饮补贴: {salary_structure.salary_structure.meal_allowance:.2f}\n"
                        f"生效日期: {salary_structure.salary_structure.effective_date}\n"
                    )
                    
                    db.session.add(record)
                    success_records.append(record)
                    print(f'成功生成员工{emp.name}的工资记录')
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f'为员工{emp.name}生成工资记录失败: {error_msg}')
                    failed_records.append({
                        'employee_id': emp.id,
                        'employee_name': emp.name,
                        'department_name': emp.department.name if emp.department else '未分配',
                        'reason': error_msg
                    })
            
            # 批量保存成功的记录
            if success_records:
                try:
                    print(f'正在保存{len(success_records)}条工资记录...')
                    db.session.commit()
                    print('保存成功')
                except Exception as e:
                    db.session.rollback()
                    error_msg = f'批量保存工资记录失败: {str(e)}'
                    print(error_msg)
                    # 将保存失败的记录移到失败列表
                    for record in success_records:
                        emp = next((e for e in employees if e.id == record.employee_id), None)
                        if emp:
                            failed_records.append({
                                'employee_id': emp.id,
                                'employee_name': emp.name,
                                'department_name': emp.department.name if emp.department else '未分配',
                                'reason': error_msg
                            })
                    success_records = []
            
            print('\n工资记录生成完成')
            print(f'成功: {len(success_records)}条')
            print(f'失败: {len(failed_records)}条')
            
            return {
                'success': [record.to_dict() for record in success_records],
                'failed': failed_records
            }
            
        except Exception as e:
            print(f'批量生成工资记录时发生错误: {str(e)}')
            return {
                'success': [],
                'failed': [{
                    'employee_id': None,
                    'employee_name': None,
                    'department_name': None,
                    'reason': f'批量生成工资记录失败: {str(e)}'
                }]
            }

    @staticmethod
    def get_salary_statistics(
        year: int = None,
        month: int = None,
        department_id: int = None,
        payment_status: str = None  # 支付状态（pending-待发放, paid-已发放）
    ) -> Dict:
        """
        获取薪资统计数据
        
        参数：
            year: 年份（必需）
            month: 月份（必需）
            department_id: 部门ID（可选）
            payment_status: 支付状态，可选值：
                - pending: 待发放
                - paid: 已发放
                - None: 不筛选支付状态，返回所有记录的统计
            
        返回：
            统计数据字典，包含：
            - total_count: 记录总数（本月记录数）
            - paid_count: 已发放记录数
            - total_basic: 基本工资总额
            - total_allowances: 补贴总额
            - total_overtime: 加班费总额
            - total_bonus: 奖金总额
            - total_tax: 个税总额
            - total_net: 实发工资总额
            - total_gross: 应发工资总额
        """
        try:
            # 确保年月参数存在
            if not year or not month:
                current_date = datetime.now()
                year = year or current_date.year
                month = month or current_date.month
                
            print(f"统计数据 - 年份: {year}, 月份: {month}")
            
            # 构建查询条件
            conditions = [
                SalaryRecord.year == year,
                SalaryRecord.month == month
            ]
            
            # 构建基础查询
            query = db.session.query(
                func.count(SalaryRecord.id).label('total_count'),
                func.sum(case((SalaryRecord.payment_status == 'paid', 1), else_=0)).label('paid_count'),
                func.coalesce(func.sum(SalaryRecord.basic_salary), 0).label('total_basic'),
                func.coalesce(func.sum(SalaryRecord.allowances), 0).label('total_allowances'),
                func.coalesce(func.sum(SalaryRecord.overtime_pay), 0).label('total_overtime'),
                func.coalesce(func.sum(SalaryRecord.bonus), 0).label('total_bonus'),
                func.coalesce(func.sum(SalaryRecord.tax), 0).label('total_tax'),
                func.coalesce(func.sum(SalaryRecord.net_salary), 0).label('total_net'),
                func.coalesce(func.sum(SalaryRecord.gross_salary), 0).label('total_gross')
            ).select_from(SalaryRecord)
            
            # 如果需要部门筛选，添加JOIN和条件
            if department_id:
                query = query.join(Employee, SalaryRecord.employee_id == Employee.id)
                conditions.append(Employee.department_id == department_id)
                
            # 添加支付状态筛选条件
            if payment_status:
                conditions.append(SalaryRecord.payment_status == payment_status)
            
            # 应用所有筛选条件
            query = query.filter(*conditions)
            
            # 执行查询
            summary = query.first()
            
            print(f"查询条件: year={year}, month={month}, department_id={department_id}, payment_status={payment_status}")
            print(f"统计结果: {summary}")
            
            if not summary or summary.total_count == 0:
                print("未找到任何记录")
                return {
                    'total_count': 0,
                    'paid_count': 0,
                    'total_basic': 0.0,
                    'total_allowances': 0.0,
                    'total_overtime': 0.0,
                    'total_bonus': 0.0,
                    'total_tax': 0.0,
                    'total_net': 0.0,
                    'total_gross': 0.0
                }
            
            # 处理结果
            result = {
                'total_count': summary.total_count or 0,
                'paid_count': summary.paid_count or 0,
                'total_basic': float(summary.total_basic or 0),
                'total_allowances': float(summary.total_allowances or 0),
                'total_overtime': float(summary.total_overtime or 0),
                'total_bonus': float(summary.total_bonus or 0),
                'total_tax': float(summary.total_tax or 0),
                'total_net': float(summary.total_net or 0),
                'total_gross': float(summary.total_gross or 0)
            }
            
            print(f"统计结果: {result}")
            return result
            
        except Exception as e:
            print(f"获取薪资统计数据时出错: {str(e)}")
            db.session.rollback()  # 发生错误时回滚事务
            # 发生错误时返回空结果
            return {
                'total_count': 0,
                'paid_count': 0,
                'total_basic': 0.0,
                'total_allowances': 0.0,
                'total_overtime': 0.0,
                'total_bonus': 0.0,
                'total_tax': 0.0,
                'total_net': 0.0,
                'total_gross': 0.0
            }

    @staticmethod
    def send_salary_slip(record_id: int) -> bool:
        """
        发送工资条邮件
        
        参数：
            record_id: 工资记录ID
            
        返回：
            发送是否成功
        """
        try:
            # 获取工资记录
            record = SalaryRecord.query.get(record_id)
            if not record:
                raise ValueError(f'工资记录不存在(ID:{record_id})')
            
            # 获取员工信息
            employee = Employee.query.get(record.employee_id)
            if not employee or not employee.email:
                raise ValueError(f'员工邮箱不存在(ID:{record.employee_id})')
            
            # 生成PDF工资条
            pdf_path = generate_pdf(record)
            
            # 发送邮件
            subject = f'{record.year}年{record.month}月工资条'
            content = f'''尊敬的{employee.name}：
                    
附件是您{record.year}年{record.month}月的工资条，请查收。

如有疑问，请联系人力资源部门。

此邮件为系统自动发送，请勿回复。'''
            
            # 使用 EmailService 发送邮件
            success, message = EmailService.send_email(
                recipient=employee.email,
                subject=subject,
                content=content,
                attachments=[pdf_path]
            )
            
            if not success:
                raise ValueError(f'发送邮件失败: {message}')
            
            return True
            
        except Exception as e:
            print(f'发送工资条失败: {str(e)}')
            return False

    @staticmethod
    def batch_send_salary_slips(
        year: int,
        month: int,
        employee_ids: List[int] = None
    ) -> Dict[str, List]:
        """
        批量发送工资条
        
        参数：
            year: 年份
            month: 月份
            employee_ids: 员工ID列表，如果为None则发送给所有有工资记录的员工
            
        返回：
            包含成功和失败记录的字典
        """
        success_ids = []
        failed_ids = []
        
        # 构建查询条件
        query = SalaryRecord.query.filter(
            SalaryRecord.year == year,
            SalaryRecord.month == month
        )
        
        if employee_ids:
            query = query.filter(SalaryRecord.employee_id.in_(employee_ids))
            
        records = query.all()
        
        for record in records:
            if SalaryService.send_salary_slip(record.id):
                success_ids.append(record.employee_id)
            else:
                failed_ids.append(record.employee_id)
                
        return {
            'success': success_ids,
            'failed': failed_ids
        }

    @staticmethod
    def update_salary_record(
        record_id: int,
        data: Dict,
        check_payment_status: bool = True
    ) -> Optional[SalaryRecord]:
        """
        更新工资记录
        
        参数：
            record_id: 工资记录ID
            data: 更新的数据字典
            check_payment_status: 是否检查支付状态，默认为True
            
        返回：
            更新后的工资记录对象
        """
        try:
            # 获取工资记录
            record = SalaryRecord.query.get(record_id)
            if not record:
                raise ValueError('工资记录不存在')
                
            # 检查支付状态
            if check_payment_status and record.payment_status == 'paid':
                raise ValueError('已支付的工资记录不能修改')
                
            # 记录原始值，用于记录变更
            original_basic_salary = float(record.basic_salary)
            original_allowances = float(record.allowances)
            original_overtime_pay = float(record.overtime_pay)
            original_bonus = float(record.bonus)
            original_deductions = float(record.deductions)
            original_gross_salary = float(record.gross_salary)
            original_tax = float(record.tax)
            original_net_salary = float(record.net_salary)
            
            # 更新基本信息
            allowed_fields = [
                'basic_salary', 'allowances', 'overtime_pay',
                'bonus', 'deductions', 'payment_status',
                'payment_date', 'remark'
            ]
            
            # 更新各个字段的值
            for field in allowed_fields:
                if field in data:
                    if field == 'payment_date' and data[field]:
                        # 处理日期字段
                        setattr(record, field, datetime.strptime(data[field], '%Y-%m-%d'))
                    elif field in ['basic_salary', 'allowances', 'overtime_pay', 'bonus', 'deductions']:
                        # 处理金额字段，确保转换为Decimal类型
                        setattr(record, field, Decimal(str(data[field])))
                    else:
                        setattr(record, field, data[field])
            
            # 重新计算工资详情
            salary_details = SalaryService.calculate_net_salary(
                basic_salary=record.basic_salary,
                allowances=record.allowances,
                overtime_pay=record.overtime_pay,
                bonus=record.bonus,
                deductions=record.deductions
            )
            
            # 更新所有金额字段
            record.gross_salary = salary_details['gross_salary']  # 更新总应发金额
            record.tax = salary_details['tax']  # 更新个人所得税
            record.net_salary = salary_details['net_salary']  # 更新实发工资
            
            # 生成变更记录
            changes = []
            if original_overtime_pay != record.overtime_pay:
                changes.append(f"加班费: {original_overtime_pay} -> {record.overtime_pay}")
            if original_gross_salary != record.gross_salary:
                changes.append(f"应发总额: {original_gross_salary} -> {record.gross_salary}")
            if original_tax != record.tax:
                changes.append(f"个税: {original_tax} -> {record.tax}")
            if original_net_salary != record.net_salary:
                changes.append(f"实发工资: {original_net_salary} -> {record.net_salary}")
            
            # 更新备注信息
            change_log = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 记录变更:\n" + "\n".join(changes)
            if record.remark:
                record.remark = record.remark + "\n" + change_log
            else:
                record.remark = change_log
            
            # 保存更改
            db.session.commit()
            return record
            
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_salary_record(record_id: int, check_payment_status: bool = True) -> bool:
        """
        删除工资记录
        
        参数：
            record_id: 工资记录ID
            check_payment_status: 是否检查支付状态，默认为True
            
        返回：
            删除是否成功
        """
        try:
            # 获取工资记录
            record = SalaryRecord.query.get(record_id)
            if not record:
                raise ValueError('工资记录不存在')
                
            # 检查支付状态
            if check_payment_status and record.payment_status == 'paid':
                raise ValueError('已支付的工资记录不能删除')
                
            # 添加删除记录到日志（如果需要的话）
            print(f'删除工资记录: ID={record_id}, 员工ID={record.employee_id}, 时间={datetime.now()}')
            
            # 执行删除
            db.session.delete(record)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def batch_update_salary_records(
        record_ids: List[int],
        data: Dict,
        check_payment_status: bool = True
    ) -> Dict[str, List]:
        """
        批量更新工资记录
        
        参数：
            record_ids: 工资记录ID列表
            data: 更新的数据字典
            check_payment_status: 是否检查支付状态，默认为True
            
        返回：
            包含成功和失败记录的字典
        """
        results = {
            'success': [],
            'failed': []
        }
        
        for record_id in record_ids:
            try:
                record = SalaryService.update_salary_record(
                    record_id=record_id,
                    data=data,
                    check_payment_status=check_payment_status
                )
                results['success'].append({
                    'id': record_id,
                    'record': record.to_dict() if record else None
                })
            except Exception as e:
                results['failed'].append({
                    'id': record_id,
                    'error': str(e)
                })
                
        return results

    @staticmethod
    def batch_delete_salary_records(
        record_ids: List[int],
        check_payment_status: bool = True
    ) -> Dict[str, List]:
        """
        批量删除工资记录
        
        参数：
            record_ids: 工资记录ID列表
            check_payment_status: 是否检查支付状态，默认为True
            
        返回：
            包含成功和失败记录的字典
        """
        results = {
            'success': [],
            'failed': []
        }
        
        for record_id in record_ids:
            try:
                success = SalaryService.delete_salary_record(
                    record_id=record_id,
                    check_payment_status=check_payment_status
                )
                if success:
                    results['success'].append(record_id)
            except Exception as e:
                results['failed'].append({
                    'id': record_id,
                    'error': str(e)
                })
                
        return results

    @staticmethod
    def batch_update_salary_records(
        employee_id: int = None,
        year: int = None,
        month: int = None,
        check_date: datetime = None,
        force_update: bool = True
    ) -> Dict[str, List]:
        """
        批量更新工资记录

        参数：
            employee_id: 员工ID，如果为None则更新所有员工
            year: 年份，如果为None则使用check_date的年份
            month: 月份，如果为None则使用check_date的月份
            check_date: 指定检查工资结构的日期，默认为当前日期
            force_update: 是否强制更新已存在的记录
            
        返回：
            包含更新成功和失败记录的字典
        """
        try:
            # 如果没有指定check_date，使用当前日期
            if not check_date:
                check_date = datetime.now()
                
            # 如果没有指定年月，使用check_date的年月
            year = year or check_date.year
            month = month or check_date.month
            
            # 获取需要更新的员工列表
            if employee_id:
                employees = [Employee.query.get(employee_id)]
                if not employees[0]:
                    raise ValueError(f'员工不存在(ID:{employee_id})')
            else:
                employees = Employee.query.all()  # 更新所有员工
            
            success_records = []
            failed_records = []
            
            for employee in employees:
                try:
                    # 重新生成工资记录
                    record = SalaryService.generate_salary_record(
                        employee_id=employee.id,
                        year=year,
                        month=month,
                        check_date=check_date,
                        force_update=force_update
                    )
                    if record:
                        success_records.append({
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'department_name': employee.department.name if employee.department else '未分配',
                            'record': record.to_dict()
                        })
                except Exception as e:
                    error_msg = str(e)
                    print(f'更新员工(ID:{employee.id})的工资记录时出错: {error_msg}')
                    failed_records.append({
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'department_name': employee.department.name if employee.department else '未分配',
                        'reason': error_msg
                    })
            
            # 提交事务
            if success_records:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    error_msg = f'提交更新失败: {str(e)}'
                    print(error_msg)
                    # 将所有记录移到失败列表
                    for record in success_records:
                        record['reason'] = error_msg
                        failed_records.append(record)
                    success_records = []
            
            return {
                'success': success_records,
                'failed': failed_records
            }
            
        except Exception as e:
            print(f'批量更新工资记录时出错: {str(e)}')
            db.session.rollback()
            raise e
