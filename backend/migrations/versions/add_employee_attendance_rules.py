"""添加员工考勤规则关联表

Revision ID: add_employee_attendance_rules
Revises: add_attendance_rule_fields
Create Date: 2024-12-18 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_employee_attendance_rules'
down_revision = 'add_attendance_rule_fields'
branch_labels = None
depends_on = None

def upgrade():
    # 创建员工考勤规则关联表
    op.create_table('employee_attendance_rules',
        sa.Column('employee_id', sa.Integer(), nullable=False, comment='员工ID'),
        sa.Column('rule_id', sa.Integer(), nullable=False, comment='考勤规则ID'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name='fk_employee_attendance_rules_employee'),
        sa.ForeignKeyConstraint(['rule_id'], ['attendance_rules.id'], name='fk_employee_attendance_rules_rule'),
        sa.PrimaryKeyConstraint('employee_id', 'rule_id')
    )

def downgrade():
    # 删除员工考勤规则关联表
    op.drop_table('employee_attendance_rules')
