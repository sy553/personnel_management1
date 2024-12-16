import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_photo(filename):
    """检查是否是允许的图片文件类型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS

def allowed_document(filename):
    """检查是否是允许的文档文件类型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS

def save_file(file, upload_folder, allowed_file_func):
    """保存上传的文件"""
    if file and allowed_file_func(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加时间戳和UUID以确保文件名唯一
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4().hex[:8])
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{timestamp}_{unique_id}.{ext}"
        
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, new_filename)
        file.save(file_path)
        
        # 返回相对路径
        return os.path.join(os.path.basename(upload_folder), new_filename)
    return None
