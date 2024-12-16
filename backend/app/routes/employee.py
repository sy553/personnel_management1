from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.employee_service import EmployeeService
from app.services.department_service import DepartmentService
from app.services.position_service import PositionService
from app.services.export_service import ExportService
from app.utils.auth import manager_required
from app.models import User, Employee, EducationHistory, WorkHistory, Department as departments_1, Position as positions_1
from app import db
from datetime import datetime, timedelta
from io import BytesIO
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes
import hashlib

# 创建员工管理蓝图
employee_bp = Blueprint('employee', __name__)

# 配置CORS
CORS(employee_bp, 
     resources={r"/*": {
         "origins": ["http://localhost:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "expose_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=True
)

# 配置静态文件存储路径
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads', 'photos')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 配置静态文件访问
employee_bp.static_folder = STATIC_FOLDER
employee_bp.static_url_path = '/static'

# 允许的图片文件扩展名和MIME类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_image_file(file):
    """检查文件是否是允许的图片类型"""
    # 检查文件扩展名
    if not ('.' in file.filename and \
           file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS):
        return False
    
    # 检查MIME类型
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False
        
    # 检查文件大小
    file.seek(0, 2)  # 移动到文件末尾
    size = file.tell()  # 获取文件大小
    file.seek(0)  # 重置文件指针
    
    return size <= MAX_FILE_SIZE

def get_file_etag(file_path):
    """生成文件的ETag"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
            return f'"{file_hash.hexdigest()}"'
    except Exception as e:
        print(f"生成ETag失败: {str(e)}")
        return None

@employee_bp.route('/static/uploads/photos/<path:filename>')
def serve_employee_photo(filename):
    """提供员工照片访问，带缓存控制"""
    try:
        # 安全检查：确保文件名不包含路径操作符
        if '..' in filename or filename.startswith('/'):
            return jsonify({
                'code': 400,
                'message': '无效的文件名',
                'data': None
            }), 400
            
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            print(f'照片文件不存在: {file_path}')
            return jsonify({
                'code': 404,
                'message': '照片不存在',
                'data': None
            }), 404

        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        etag = get_file_etag(file_path)

        # 检查条件请求
        if_none_match = request.headers.get('If-None-Match')
        if_modified_since = request.headers.get('If-Modified-Since')
        
        if if_none_match and etag and if_none_match == etag:
            return '', 304
            
        if if_modified_since:
            try:
                ims_dt = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
                if file_mtime <= ims_dt:
                    return '', 304
            except ValueError:
                pass

        # 准备响应
        response = send_file(file_path)
        
        # 设置缓存控制头
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1年
        response.headers['ETag'] = etag
        response.headers['Last-Modified'] = file_mtime.strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['Expires'] = (datetime.now() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 设置正确的Content-Type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            response.headers['Content-Type'] = mime_type
        
        # 设置Content-Length
        response.headers['Content-Length'] = file_size
        
        return response
        
    except Exception as e:
        print(f'照片访问失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'照片访问失败: {str(e)}',
            'data': None
        }), 500

@employee_bp.route('/employees', methods=['POST'])
@jwt_required()
@manager_required()
def create_employee():
    """创建新员工"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['employee_id', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"缺少必要字段: {field}"}), 400
            
    # 创建员工
    employee, error = EmployeeService.create_employee(data)
    if error:
        return jsonify({"msg": error}), 400
        
    return jsonify({
        "msg": "创建成功",
        "employee": {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "name": employee.name
        }
    }), 201

@employee_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@jwt_required()
@manager_required()
def update_employee(employee_id):
    """更新员工信息"""
    try:
        data = request.get_json()
        
        # 更新员工信息
        employee, error = EmployeeService.update_employee(employee_id, data)
        if error:
            return jsonify({
                "code": 400,
                "msg": error,
                "data": None
            }), 400
            
        return jsonify({
            "code": 200,
            "msg": "更新成功",
            "data": {
                "employee": employee.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"更新员工失败: {str(e)}",
            "data": None
        }), 500

@employee_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@jwt_required()
@manager_required()
def delete_employee(employee_id):
    """删除员工（软删除）"""
    success, error = EmployeeService.delete_employee(employee_id)
    if error:
        return jsonify({"msg": error}), 400
        
    return jsonify({"msg": "删除成功"})

@employee_bp.route('/employees/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """获取单个员工信息"""
    employee, error = EmployeeService.get_employee(employee_id)
    if error:
        return jsonify({"code": 400, "msg": error}), 404
        
    return jsonify({
        "code": 200,
        "msg": "success",
        "data": employee.to_dict() if employee else None
    })

@employee_bp.route('/employees', methods=['GET'])
def get_employees():
    """获取员工列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        department_id = request.args.get('department_id', type=int)
        position_id = request.args.get('position_id', type=int)
        gender = request.args.get('gender')
        education = request.args.get('education')
        employment_status = request.args.get('employment_status', 'active')
        
        print("请求参数:")
        print(f"page: {page}")
        print(f"per_page: {per_page}")
        print(f"search: {search}")
        print(f"department_id: {department_id}")
        print(f"position_id: {position_id}")
        print(f"education: {education}")
        print(f"employment_status: {employment_status}")
        
        # 构建基础查询
        query = db.session.query(
            Employee.id,
            Employee.employee_id,
            Employee.name,
            Employee.gender,
            Employee.photo_url,
            Employee.employment_status,
            Employee.department_id,
            Employee.position_id,
            departments_1.name.label('department_name'),
            positions_1.name.label('position_name')
        ).select_from(Employee).\
        outerjoin(departments_1, departments_1.id == Employee.department_id).\
        outerjoin(positions_1, positions_1.id == Employee.position_id)
        
        # 添加筛选条件
        if employment_status:
            print(f"正在筛选状态为 {employment_status} 的员工")
            query = query.filter(Employee.employment_status == employment_status)
            
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(db.or_(
                Employee.name.ilike(search_pattern),
                Employee.employee_id.ilike(search_pattern)
            ))
            
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        if position_id:
            query = query.filter(Employee.position_id == position_id)
            
        if gender:
            query = query.filter(Employee.gender == gender)
            
        if education:
            query = query.filter(Employee.education == education)
            
        # 获取总数
        total = query.count()
        
        # 分页
        query = query.order_by(Employee.id.desc()).\
                paginate(page=page, per_page=per_page, error_out=False)
        
        employees = query.items
        
        print("SQL查询:")
        print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))
        print("\n查询结果: 总数", total)
        for emp in employees:
            print(f"ID: {emp.id}, Name: {emp.name}, Status: {emp.employment_status}")
        
        return jsonify({
            "code": 200,
            "msg": "获取员工列表成功",
            "data": {
                "items": [{
                    "id": emp.id,
                    "employee_id": emp.employee_id,
                    "name": emp.name,
                    "gender": emp.gender,
                    "photo_url": emp.photo_url,
                    "employment_status": emp.employment_status,
                    "department": {
                        "id": emp.department_id,
                        "name": emp.department_name
                    } if emp.department_id else None,
                    "position": {
                        "id": emp.position_id,
                        "name": emp.position_name
                    } if emp.position_id else None
                } for emp in employees],
                "total": total,
                "page": page,
                "per_page": per_page
            }
        })
    except Exception as e:
        print(f"获取员工列表出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"获取员工列表失败: {str(e)}",
            "data": None
        }), 500

# 部门相关路由
@employee_bp.route('/departments', methods=['POST'])
@jwt_required()
@manager_required()
def create_department():
    """创建新部门"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少部门名称",
                "data": None
            }), 400
            
        department, error = DepartmentService.create_department(data)
        if error:
            return jsonify({
                "code": 400,
                "message": error,
                "data": None
            }), 400
            
        return jsonify({
            "code": 200,
            "message": "创建成功",
            "data": {
                "department": {
                    "id": department.id,
                    "name": department.name,
                    "description": department.description,
                    "parent_id": department.parent_id,
                    "manager_id": department.manager_id
                }
            }
        }), 201
    except Exception as e:
        print(f"创建部门时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "创建部门失败，请稍后重试",
            "error": str(e),
            "data": None
        }), 500

@employee_bp.route('/departments', methods=['GET'])
def get_departments():
    """获取部门列表"""
    try:
        departments = DepartmentService.get_departments()
        return jsonify({
            "code": 200,
            "msg": "获取部门列表成功",
            "data": [dept.to_dict() for dept in departments] if departments else []
        })
    except Exception as e:
        print(f"获取部门列表出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"获取部门列表失败: {str(e)}",
            "data": None
        }), 500

@employee_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@jwt_required()
@manager_required()
def delete_department(department_id):
    """删除部门"""
    try:
        success, error = DepartmentService.delete_department(department_id)
        if error:
            return jsonify({
                "code": 400,
                "msg": error
            }), 400
            
        return jsonify({
            "code": 200,
            "msg": "删除成功"
        })
    except Exception as e:
        print(f"删除部门时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "删除部门失败，请稍后重试"
        }), 500

@employee_bp.route('/departments/<int:department_id>', methods=['PUT'])
@jwt_required()
@manager_required()
def update_department(department_id):
    """更新部门信息"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({
                "code": 400,
                "msg": "缺少部门名称"
            }), 400
            
        # 检查是否存在循环引用
        if data.get('parent_id') == department_id:
            return jsonify({
                "code": 400,
                "msg": "部门不能作为自己的父部门"
            }), 400
            
        department, error = DepartmentService.update_department(department_id, data)
        if error:
            return jsonify({
                "code": 400,
                "msg": error
            }), 400
            
        return jsonify({
            "code": 200,
            "msg": "更新成功",
            "data": {
                "department": {
                    "id": department.id,
                    "name": department.name,
                    "description": department.description,
                    "parent_id": department.parent_id,
                    "manager_id": department.manager_id
                }
            }
        })
    except Exception as e:
        print(f"更新部门时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "更新部门失败，请稍后重试"
        }), 500

# 职位相关路由
@employee_bp.route('/positions', methods=['POST'])
@jwt_required()
@manager_required()
def create_position():
    """创建新职位"""
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({"msg": "缺���职位名称"}), 400
        
    position, error = PositionService.create_position(data)
    if error:
        return jsonify({"msg": error}), 400
        
    return jsonify({
        "msg": "创建成功",
        "position": {
            "id": position.id,
            "name": position.name
        }
    }), 201

@employee_bp.route('/positions', methods=['GET'])
def get_positions():
    """获取职位列表"""
    try:
        positions = PositionService.get_positions()
        return jsonify({
            "code": 200,
            "msg": "获取职位列表成功",
            "data": [pos.to_dict() for pos in positions] if positions else []
        })
    except Exception as e:
        print(f"获取职位列表出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"获取职位列表失败: {str(e)}",
            "data": None
        }), 500

# 导入导出相关路由
@employee_bp.route('/employees/export', methods=['GET'])
@jwt_required()
def export_employees():
    """导出员工数据为Excel"""
    try:
        excel_data = ExportService.export_employees_to_excel()
        
        # 生成文件名
        filename = f'employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@employee_bp.route('/employees/import', methods=['POST'])
@jwt_required()
@manager_required()
def import_employees():
    """从Excel导入员工数据"""
    print("开始处理文件导入请求")  # 添加日志
    
    if 'file' not in request.files:
        print("未找到上传的文件")  # 添加日志
        return jsonify({"msg": "没有上传文件"}), 400
        
    file = request.files['file']
    print(f"接收到文件: {file.filename}")  # 添加日志
    
    if not file.filename:
        print("文件名为空")  # 添加日志
        return jsonify({"msg": "没有选择文件"}), 400
        
    if not file.filename.endswith('.xlsx'):
        print(f"不支持的文件类型: {file.filename}")  # 添加日志
        return jsonify({"msg": "只支持.xlsx格式的Excel文件"}), 400
        
    try:
        print("开始解析Excel文件")  # 添加日志
        # 解析Excel文件
        result = ExportService.parse_excel_to_employees(file)
        print(f"Excel解析结果: {result}")  # 添加日志
        
        # 如果只有错误，没有成功的数据
        if not result['employees'] and result['errors']:
            print(f"解析失败，错误: {result['errors']}")  # 添加日志
            return jsonify({
                "msg": "导入失败",
                "success_count": 0,
                "errors": result['errors']
            }), 400
            
        # 批量创建员工
        success_count = 0
        errors = result['errors']  # 保留解析时的错误
        
        print(f"开始导入 {len(result['employees'])} 条数据")  # 添加日志
        for employee_data in result['employees']:
            try:
                print(f"正在导入员工: {employee_data.get('name', 'Unknown')}")  # 添加日志
                employee, error = EmployeeService.create_employee(employee_data)
                if error:
                    print(f"导入失败: {error}")  # 添加日志
                    errors.append(f"员工 {employee_data['name']} ({employee_data['employee_id']}) 导入失败: {error}")
                else:
                    success_count += 1
                    print(f"导入成功: {employee_data.get('name', 'Unknown')}")  # 添加日志
            except Exception as e:
                print(f"导入异常: {str(e)}")  # 添加日志
                errors.append(f"员工 {employee_data['name']} ({employee_data['employee_id']}) 导入失败: {str(e)}")
        
        print(f"导入完成: 成功 {success_count} 条, 失败 {len(errors)} 条")  # 添加日志
        
        # 根据导入结果返回不同的状态码
        if success_count == 0:
            return jsonify({
                "msg": "所有数据导入失败",
                "success_count": 0,
                "errors": errors
            }), 400
        elif errors:
            return jsonify({
                "msg": f"部分数据导入成功",
                "success_count": success_count,
                "total_count": len(result['employees']),
                "errors": errors
            }), 207  # 207 Multi-Status
        else:
            return jsonify({
                "msg": f"成功导入 {success_count} 名员工",
                "success_count": success_count,
                "total_count": success_count,
                "errors": []
            })
    except ValueError as e:
        print(f"值错误: {str(e)}")  # 添加日志
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        print(f"导入过程发生异常: {str(e)}")  # 添加日志
        return jsonify({"msg": f"导入失败: {str(e)}"}), 500

@employee_bp.route('/employees/import-template', methods=['GET'])
@jwt_required()
def get_import_template():
    """获取导入模板"""
    try:
        template_data = ExportService.get_import_template()
        
        return send_file(
            BytesIO(template_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='employee_import_template.xlsx'
        )
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@employee_bp.route('/init-data', methods=['POST'])
@jwt_required()
@manager_required()
def init_data():
    """初始化基础数据"""
    try:
        # 初始化部门数据
        dept_error, departments = DepartmentService.init_departments()
        if dept_error:
            return jsonify({"message": dept_error}), 400

        # 初始化职位数据
        pos_error, positions = PositionService.init_positions()
        if pos_error:
            return jsonify({"message": pos_error}), 400

        return jsonify({
            "code": 200,
            "message": "初始化成功",
            "data": {
                "departments": len(departments) if departments else 0,
                "positions": len(positions) if positions else 0
            }
        })
    except Exception as e:
        print(f"初始化数据时出错: {str(e)}")
        return jsonify({"message": "初始化数据失败"}), 500

@employee_bp.route('/employees/upload/photo/<int:employee_id>', methods=['POST', 'OPTIONS'])
@jwt_required()
def upload_employee_photo(employee_id):
    """上传员工照片"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print(f"Received photo upload request for employee: {employee_id}")
        print(f"Files in request: {request.files}")
        print(f"Form data: {request.form}")
        
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '没有上传文件',
                'data': None
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '没有选择文件',
                'data': None
            }), 400
            
        if not allowed_image_file(file):
            return jsonify({
                'code': 400,
                'message': '不支持的文件类型或文件大小超过限制(5MB)',
                'data': None
            }), 400
            
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = os.path.splitext(secure_filename(file.filename))[0]
        filename = f"{base_filename}_{timestamp}{os.path.splitext(file.filename)[1]}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"Saving file to: {file_path}")
        file.save(file_path)
        
        # 构建相对URL路径
        photo_url = f'/static/uploads/photos/{filename}'
        print(f"Successfully saved photo, URL: {photo_url}")
        
        # 更新员工照片信息
        employee = Employee.query.get(employee_id)
        if employee:
            # 如果存在旧照片，删除它
            if employee.photo_url:
                old_photo = os.path.join(UPLOAD_FOLDER, os.path.basename(employee.photo_url))
                if os.path.exists(old_photo):
                    os.remove(old_photo)
            
            employee.photo_url = photo_url
            db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '照片上传成功',
            'data': {
                'photo_url': photo_url
            }
        })
    except Exception as e:
        print(f'照片上传失败: {str(e)}')
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'照片上传失败: {str(e)}',
            'data': None
        }), 500

# 教育经历相关路由
@employee_bp.route('/employees/<int:employee_id>/education', methods=['GET'])
@jwt_required()
def get_education_history(employee_id):
    """获取员工教育经历"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        education_history = employee.education_history
        return jsonify({
            'code': 200,
            'data': [edu.to_dict() for edu in education_history]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>/education', methods=['POST'])
@jwt_required()
def create_education_history(employee_id):
    """创建教育经历"""
    try:
        data = request.get_json()
        employee = Employee.query.get_or_404(employee_id)
        education = EducationHistory(
            employee_id=employee_id,
            school=data.get('school'),
            major=data.get('major'),
            degree=data.get('degree'),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None
        )
        db.session.add(education)
        db.session.commit()
        return jsonify({'code': 200, 'data': education.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>/education/<int:edu_id>', methods=['DELETE'])
@jwt_required()
def delete_education_history(employee_id, edu_id):
    """删除教育经历"""
    try:
        education = EducationHistory.query.get_or_404(edu_id)
        if education.employee_id != employee_id:
            return jsonify({'code': 403, 'message': '无权限操作'}), 403
        db.session.delete(education)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 工作经历相关路由
@employee_bp.route('/employees/<int:employee_id>/work', methods=['GET'])
@jwt_required()
def get_work_history(employee_id):
    """获取员工工作经历"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        work_history = employee.work_history
        return jsonify({
            'code': 200,
            'data': [work.to_dict() for work in work_history]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>/work', methods=['POST'])
@jwt_required()
def create_work_history(employee_id):
    """创建工作经历"""
    try:
        data = request.get_json()
        employee = Employee.query.get_or_404(employee_id)
        work = WorkHistory(
            employee_id=employee_id,
            company=data.get('company'),
            position=data.get('position'),
            description=data.get('description'),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None
        )
        db.session.add(work)
        db.session.commit()
        return jsonify({'code': 200, 'data': work.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>/work/<int:work_id>', methods=['DELETE'])
@jwt_required()
def delete_work_history(employee_id, work_id):
    """删除工作经历"""
    try:
        work = WorkHistory.query.get_or_404(work_id)
        if work.employee_id != employee_id:
            return jsonify({'code': 403, 'message': '无权限操作'}), 403
        db.session.delete(work)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500
