"""添加考勤规则新字段

Revision ID: update_attendance_rules_v2
Revises: 07f77f7323f7
Create Date: 2024-12-18 10:42:15.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, time

# revision identifiers, used by Alembic.
revision = 'update_attendance_rules_v2'
down_revision = '07f77f7323f7'
branch_labels = None
depends_on = None

def upgrade():
    # 添加新字段到考勤规则表
    op.add_column('attendance_rules', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('attendance_rules', sa.Column('effective_start_date', sa.Date(), nullable=True))
    op.add_column('attendance_rules', sa.Column('effective_end_date', sa.Date(), nullable=True))
    op.add_column('attendance_rules', sa.Column('flexible_time', sa.Integer(), nullable=True))
    op.add_column('attendance_rules', sa.Column('break_start_time', sa.Time(), nullable=True))
    op.add_column('attendance_rules', sa.Column('break_end_time', sa.Time(), nullable=True))
    op.add_column('attendance_rules', sa.Column('overtime_rate', sa.Float(), nullable=True))
    op.add_column('attendance_rules', sa.Column('weekend_overtime_rate', sa.Float(), nullable=True))
    op.add_column('attendance_rules', sa.Column('holiday_overtime_rate', sa.Float(), nullable=True))
    
    # 添加外键约束
    op.create_foreign_key(
        'fk_attendance_rules_department',
        'attendance_rules', 'departments',
        ['department_id'], ['id']
    )
    
    # 设置默认值
    op.execute("UPDATE attendance_rules SET effective_start_date = CURDATE() WHERE effective_start_date IS NULL")
    op.execute("UPDATE attendance_rules SET flexible_time = 30 WHERE flexible_time IS NULL")
    op.execute("UPDATE attendance_rules SET overtime_rate = 1.5 WHERE overtime_rate IS NULL")
    op.execute("UPDATE attendance_rules SET weekend_overtime_rate = 2.0 WHERE weekend_overtime_rate IS NULL")
    op.execute("UPDATE attendance_rules SET holiday_overtime_rate = 3.0 WHERE holiday_overtime_rate IS NULL")
    
    # 修改effective_start_date为非空
    op.alter_column('attendance_rules', 'effective_start_date',
                    existing_type=sa.Date(),
                    nullable=False)
    
    # 检查是否存在默认规则，如果不存在则创建
    conn = op.get_bind()
    result = conn.execute("SELECT COUNT(*) FROM attendance_rules WHERE is_default = true").scalar()
    if result == 0:
        # 创建默认规则
        conn.execute("""
            INSERT INTO attendance_rules (
                name, work_start_time, work_end_time, 
                late_threshold, early_leave_threshold, overtime_minimum,
                is_default, description, effective_start_date,
                flexible_time, overtime_rate, weekend_overtime_rate,
                holiday_overtime_rate, created_at, updated_at
            ) VALUES (
                '默认考勤规则', '09:00:00', '18:00:00',
                15, 15, 60,
                true, '系统默认考勤规则', CURDATE(),
                30, 1.5, 2.0,
                3.0, NOW(), NOW()
            )
        """)

def downgrade():
    # 删除外键约束
    op.drop_constraint('fk_attendance_rules_department', 'attendance_rules', type_='foreignkey')
    
    # 删除新增的字段
    op.drop_column('attendance_rules', 'holiday_overtime_rate')
    op.drop_column('attendance_rules', 'weekend_overtime_rate')
    op.drop_column('attendance_rules', 'overtime_rate')
    op.drop_column('attendance_rules', 'break_end_time')
    op.drop_column('attendance_rules', 'break_start_time')
    op.drop_column('attendance_rules', 'flexible_time')
    op.drop_column('attendance_rules', 'effective_end_date')
    op.drop_column('attendance_rules', 'effective_start_date')
    op.drop_column('attendance_rules', 'department_id')
