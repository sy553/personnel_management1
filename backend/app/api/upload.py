import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.employee import ContractAttachment

bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/api/upload/photo', methods=['POST'])
def upload_photo():
    """上传员工照片"""
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'msg': '没有文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': 400, 'msg': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'msg': '不支持的文件类型'})
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 生成唯一的文件名
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 返回文件URL
        file_url = f"/uploads/photos/{unique_filename}"
        return jsonify({
            'code': 200,
            'data': {
                'url': file_url
            },
            'msg': '上传成功'
        })
    except Exception as e:
        print('上传照片失败:', str(e))
        return jsonify({'code': 500, 'msg': f'上传失败: {str(e)}'})

@bp.route('/api/upload/contract', methods=['POST'])
def upload_contract():
    """上传合同附件"""
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'msg': '没有文件'})
        
        file = request.files['file']
        employee_id = request.form.get('employee_id')
        
        if file.filename == '':
            return jsonify({'code': 400, 'msg': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'msg': '不支持的文件类型'})
        
        if not employee_id:
            return jsonify({'code': 400, 'msg': '缺少员工ID'})
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 生成唯一的文件名
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'contracts')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 保存文件信息到数据库
        file_url = f"/uploads/contracts/{unique_filename}"
        attachment = ContractAttachment(
            employee_id=employee_id,
            file_name=filename,
            file_url=file_url,
            file_type=filename.rsplit('.', 1)[1].lower()
        )
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': attachment.to_dict(),
            'msg': '上传成功'
        })
    except Exception as e:
        db.session.rollback()
        print('上传合同失败:', str(e))
        return jsonify({'code': 500, 'msg': f'上传失败: {str(e)}'})

@bp.route('/api/attachments/<int:employee_id>', methods=['GET'])
def get_attachments(employee_id):
    """获取员工的所有合同附件"""
    try:
        attachments = ContractAttachment.query.filter_by(employee_id=employee_id).all()
        return jsonify({
            'code': 200,
            'data': [attachment.to_dict() for attachment in attachments],
            'msg': '获取成功'
        })
    except Exception as e:
        print('获取附件失败:', str(e))
        return jsonify({'code': 500, 'msg': f'获取失败: {str(e)}'})
