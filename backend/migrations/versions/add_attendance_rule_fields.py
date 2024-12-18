"""添加考勤规则优先级和类型字段

Revision ID: add_attendance_rule_fields
Revises: update_attendance_rules_v2
Create Date: 2024-12-18 10:50:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_attendance_rule_fields'
down_revision = 'update_attendance_rules_v2'
branch_labels = None
depends_on = None

def upgrade():
    # 添加新字段
    op.add_column('attendance_rules', sa.Column('priority', sa.Integer(), nullable=True))
    op.add_column('attendance_rules', sa.Column('rule_type', sa.String(20), nullable=True))
    
    # 设置默认值
    op.execute("UPDATE attendance_rules SET priority = 0 WHERE priority IS NULL")
    op.execute("UPDATE attendance_rules SET rule_type = 'regular' WHERE rule_type IS NULL")

def downgrade():
    # 删除新增的字段
    op.drop_column('attendance_rules', 'rule_type')
    op.drop_column('attendance_rules', 'priority')
