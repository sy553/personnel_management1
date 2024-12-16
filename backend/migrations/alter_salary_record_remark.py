import os
import sys
from sqlalchemy import text

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from app import create_app, db

def alter_salary_record_remark():
    """
    修改salary_records表的remark字段长度为1000
    """
    # 创建应用上下文
    app = create_app()
    
    try:
        with app.app_context():
            # 使用text()函数包装SQL语句
            sql = text("ALTER TABLE salary_records MODIFY COLUMN remark VARCHAR(1000) COMMENT '备注'")
            db.session.execute(sql)
            db.session.commit()
            print("成功修改salary_records表的remark字段长度为1000")
    except Exception as e:
        print(f"修改字段失败: {str(e)}")
        with app.app_context():
            db.session.rollback()

if __name__ == '__main__':
    alter_salary_record_remark()
