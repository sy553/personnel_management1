"""add attendance rules table

Revision ID: 2024_12_17_add_attendance_rules
Revises: c95f1ed126f7
Create Date: 2024-12-17 14:30:45

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2024_12_17_add_attendance_rules'
down_revision = 'c95f1ed126f7'
branch_labels = None
depends_on = None

def upgrade():
    # 创建考勤规则表
    op.create_table('attendance_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('work_start_time', sa.Time(), nullable=False),
        sa.Column('work_end_time', sa.Time(), nullable=False),
        sa.Column('late_threshold', sa.Integer(), nullable=True),
        sa.Column('early_leave_threshold', sa.Integer(), nullable=True),
        sa.Column('overtime_minimum', sa.Integer(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 添加默认考勤规则
    op.execute("""
        INSERT INTO attendance_rules (
            name, work_start_time, work_end_time, 
            late_threshold, early_leave_threshold, overtime_minimum,
            is_default, description, created_at, updated_at
        ) VALUES (
            '默认规则', '09:00:00', '18:00:00',
            15, 15, 60,
            1, '标准工作时间：9:00-18:00，午休：12:00-13:00',
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
    """)

def downgrade():
    # 删除考勤规则表
    op.drop_table('attendance_rules')
