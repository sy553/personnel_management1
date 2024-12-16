import pandas as pd
from io import BytesIO
from datetime import datetime
from app.models import Employee, Department, Position

class ExportService:
    @staticmethod
    def export_employees_to_excel():
        """
        将员工数据导出为Excel文件
        :return: Excel文件的二进制数据
        """
        try:
            # 获取所有员工数据
            employees = Employee.query.all()
            departments = {dept.id: dept.name for dept in Department.query.all()}
            positions = {pos.id: pos.name for pos in Position.query.all()}

            # 准备数据
            data = []
            for emp in employees:
                data.append({
                    '员工编号': emp.employee_id,
                    '姓名': emp.name,
                    '性别': '男' if emp.gender == 'male' else '女' if emp.gender == 'female' else '',
                    '出生日期': emp.birth_date.strftime('%Y-%m-%d') if emp.birth_date else '',
                    '身份证号': emp.id_card or '',
                    '联系电话': emp.phone or '',
                    '住址': emp.address or '',
                    '部门': departments.get(emp.department_id, ''),
                    '职位': positions.get(emp.position_id, ''),
                    '入职日期': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                    '在职状态': {
                        'active': '在职',
                        'resigned': '离职',
                        'suspended': '休假'
                    }.get(emp.employment_status, '')
                })

            # 创建DataFrame
            df = pd.DataFrame(data)

            # 将DataFrame写入Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='员工信息')
            
            return output.getvalue()
        except Exception as e:
            raise Exception(f"导出Excel失败: {str(e)}")

    @staticmethod
    def parse_excel_to_employees(file_data):
        """
        从Excel文件解析员工数据
        :param file_data: Excel文件数据
        :return: 解析后的员工数据列表
        """
        try:
            print("开始读取Excel文件")  # 添加日志
            # 读取Excel文件
            df = pd.read_excel(file_data)
            print(f"Excel文件读取成功，包含 {len(df)} 行数据")  # 添加日志

            # 检查必要的列是否存在
            required_columns = ['员工编号', '姓名', '部门', '职位', '身份证号']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Excel文件缺少必要的列: {', '.join(missing_columns)}"
                print(error_msg)  # 添加日志
                raise ValueError(error_msg)

            # 获取部门和职位的映射
            print("获取部门和职位映射")  # 添加日志
            departments = {dept.name.strip(): dept.id for dept in Department.query.all()}
            positions = {pos.name.strip(): pos.id for pos in Position.query.all()}
            print(f"可用部门: {list(departments.keys())}")  # 添加日志
            print(f"可用职位: {list(positions.keys())}")  # 添加日志

            # 获取已存在的员工号和身份证号
            existing_employees = Employee.query.all()
            existing_employee_ids = {emp.employee_id for emp in existing_employees}
            existing_id_cards = {emp.id_card for emp in existing_employees if emp.id_card}
            print(f"已存在的员工号: {existing_employee_ids}")  # 添加日志
            print(f"已存在的身份证号数量: {len(existing_id_cards)}")  # 添加日志

            # 检查Excel中是否有重复的身份证号
            excel_id_cards = df['身份证号'].dropna().astype(str).str.strip()
            duplicate_id_cards = excel_id_cards[excel_id_cards.duplicated()].unique()
            if len(duplicate_id_cards) > 0:
                error_msg = f"Excel文件中存在重复的身份证号: {', '.join(duplicate_id_cards)}"
                print(error_msg)  # 添加日志
                raise ValueError(error_msg)

            # 解析数据
            employees = []
            errors = []
            for index, row in df.iterrows():
                try:
                    # 验证必填字段
                    if pd.isna(row['员工编号']) or pd.isna(row['姓名']) or pd.isna(row['身份证号']):
                        raise ValueError('员工编号、姓名和身份证号为必填项')

                    # 验证员工号是否已存在
                    employee_id = str(row['员工编号']).strip()
                    if employee_id in existing_employee_ids:
                        raise ValueError(f'员工号 {employee_id} 已存在')

                    # 验证身份证号是否已存在
                    id_card = str(row['身份证号']).strip()
                    if id_card in existing_id_cards:
                        raise ValueError(f'身份证号 {id_card} 已存在')

                    # 清理和验证部门
                    department = row['部门'].strip() if pd.notna(row['部门']) else None
                    if not department:
                        raise ValueError('部门不能为空')
                    if department not in departments:
                        raise ValueError(f"无效的部门名称: {department}, 可用部门: {list(departments.keys())}")

                    # 清理和验证职位
                    position = row['职位'].strip() if pd.notna(row['职位']) else None
                    if not position:
                        raise ValueError('职位不能为空')
                    if position not in positions:
                        raise ValueError(f"无效的职位名称: {position}, 可用职位: {list(positions.keys())}")

                    # 处理日期格式
                    birth_date = None
                    hire_date = None
                    try:
                        if pd.notna(row['出生日期']):
                            birth_date = pd.to_datetime(row['出生日期']).date()
                        if pd.notna(row['入职日期']):
                            hire_date = pd.to_datetime(row['入职日期']).date()
                    except Exception as e:
                        raise ValueError(f"日期格式错误: {str(e)}")

                    # 处理性别
                    gender_map = {'男': 'male', '女': 'female'}
                    gender = None
                    if pd.notna(row['性别']):
                        if row['性别'] not in gender_map:
                            raise ValueError(f"无效的性别值: {row['性别']}, 应为: 男 或 女")
                        gender = gender_map[row['性别']]
                    
                    # 处理在职状态
                    status_map = {'在职': 'active', '离职': 'resigned', '休假': 'suspended'}
                    status = 'active'
                    if pd.notna(row['在职状态']):
                        if row['在职状态'] not in status_map:
                            raise ValueError(f"无效的在职状态: {row['在职状态']}, 应为: 在职、离职 或 休假")
                        status = status_map[row['在职状态']]

                    # 创建员工数据
                    employee = {
                        'employee_id': employee_id,
                        'name': str(row['姓名']).strip(),
                        'gender': gender,
                        'birth_date': birth_date,
                        'id_card': id_card,
                        'phone': str(row['联系电话']).strip() if pd.notna(row['联系电话']) else None,
                        'address': str(row['住址']).strip() if pd.notna(row['住址']) else None,
                        'department_id': departments[department],
                        'position_id': positions[position],
                        'hire_date': hire_date,
                        'employment_status': status
                    }

                    # 验证手机号格式（如果有）
                    if employee['phone'] and not employee['phone'].isdigit():
                        raise ValueError('手机号必须为数字')

                    print(f"成功解析第 {index + 2} 行数据: {employee['name']}")  # 添加日志
                    employees.append(employee)
                    # 添加到已存在的集合中，防止重复
                    existing_employee_ids.add(employee_id)
                    existing_id_cards.add(id_card)
                except Exception as e:
                    error_msg = f"第{index + 2}行数据解析失败: {str(e)}"
                    print(error_msg)  # 添加日志
                    errors.append(error_msg)

            print(f"Excel解析完成: 成功 {len(employees)} 条, 失败 {len(errors)} 条")  # 添加日志
            if not employees and errors:
                raise ValueError("所有数据均解析失败")

            return {
                'employees': employees,
                'errors': errors
            }
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            error_msg = f"解析Excel失败: {str(e)}"
            print(error_msg)  # 添加日志
            raise ValueError(error_msg)

    @staticmethod
    def get_import_template():
        """
        生成导入模板
        :return: Excel模板文件的二进制数据
        """
        try:
            # 获取可用的部门和职位
            departments = [dept.name.strip() for dept in Department.query.all()]
            positions = [pos.name.strip() for pos in Position.query.all()]

            # 准备模板数据
            template_data = {
                '员工编号': ['示例：EMP001'],
                '姓名': ['张三'],
                '性别': ['男/女'],
                '出生日期': ['1990-01-01'],
                '身份证号': ['110101199001011234'],
                '联系电话': ['13800138000'],
                '住址': ['北京市朝阳区xx街xx号'],
                '部门': [departments[0] if departments else '技术部'],
                '职位': [positions[0] if positions else '软件工程师'],
                '入职日期': ['2020-01-01'],
                '在职状态': ['在职/离职/休假']
            }

            # 创建DataFrame
            df = pd.DataFrame(template_data)

            # 添加数据验证说明
            with pd.ExcelWriter(BytesIO(), engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='员工信息模板')
                
                # 获取工作表
                worksheet = writer.sheets['员工信息模板']
                
                # 添加说明
                notes = [
                    '',
                    '填表说明：',
                    '1. 标记*的字段为必填项',
                    f'2. 可用部门：{", ".join(departments)}',
                    f'3. 可用职位：{", ".join(positions)}',
                    '4. 日期格式：YYYY-MM-DD',
                    '5. 性别：男/女',
                    '6. 在职状态：在职/离职/休假'
                ]
                
                for i, note in enumerate(notes, start=len(df) + 3):
                    worksheet.cell(row=i, column=1, value=note)
                
                # 获取输出
                output = BytesIO()
                writer.book.save(output)
                output.seek(0)
                return output.getvalue()

        except Exception as e:
            print(f"生成模板失败: {str(e)}")  # 添加日志
            raise Exception(f"生成模板失败: {str(e)}")
