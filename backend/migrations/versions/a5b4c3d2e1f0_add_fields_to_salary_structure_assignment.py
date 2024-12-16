"""添加is_active和expiry_date字段到工资结构分配表

Revision ID: a5b4c3d2e1f0
Revises: fcbedd8f4f75
Create Date: 2024-12-15 00:56:16.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'a5b4c3d2e1f0'
down_revision = 'fcbedd8f4f75'  # 确保这个值与最新的迁移版本一致
branch_labels = None
depends_on = None

def upgrade():
    """
    升级数据库结构
    添加is_active和expiry_date字段到salary_structure_assignments表
    """
    # 添加is_active字段，默认值为True
    op.add_column('salary_structure_assignments',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1', comment='是否激活')
    )
    
    # 添加expiry_date字段，允许为空
    op.add_column('salary_structure_assignments',
        sa.Column('expiry_date', sa.Date(), nullable=True, comment='失效日期')
    )

def downgrade():
    """
    回滚数据库结构
    删除新添加的字段
    """
    # 删除expiry_date字段
    op.drop_column('salary_structure_assignments', 'expiry_date')
    
    # 删除is_active字段
    op.drop_column('salary_structure_assignments', 'is_active')
