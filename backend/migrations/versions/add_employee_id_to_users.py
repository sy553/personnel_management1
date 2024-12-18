"""添加员工ID到用户表

Revision ID: add_employee_id_to_users
Revises: add_employee_attendance_rules
Create Date: 2024-12-18 16:11:14.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_employee_id_to_users'
down_revision = 'add_employee_attendance_rules'
branch_labels = None
depends_on = None

def upgrade():
    """升级数据库"""
    # 添加employee_id字段
    op.add_column('users', sa.Column('employee_id', sa.Integer(), nullable=True))
    
    # 添加外键约束
    op.create_foreign_key(
        'fk_users_employee_id',
        'users',
        'employees',
        ['employee_id'],
        ['id']
    )

def downgrade():
    """降级数据库"""
    # 删除外键约束
    op.drop_constraint('fk_users_employee_id', 'users', type_='foreignkey')
    
    # 删除employee_id字段
    op.drop_column('users', 'employee_id')
