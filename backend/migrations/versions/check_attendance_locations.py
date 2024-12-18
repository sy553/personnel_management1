"""check and update attendance locations table

Revision ID: check_attendance_locations
Revises: add_employee_id_to_users
Create Date: 2024-12-18 16:54:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'check_attendance_locations'
down_revision = 'add_employee_id_to_users'
branch_labels = None
depends_on = None

def upgrade():
    # 获取数据库连接
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    
    # 检查表是否存在
    if 'attendance_locations' not in inspector.get_table_names():
        # 如果表不存在，创建表
        op.create_table(
            'attendance_locations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False, comment='地点名称'),
            sa.Column('address', sa.String(length=255), nullable=False, comment='详细地址'),
            sa.Column('latitude', sa.Float(), nullable=False, comment='纬度'),
            sa.Column('longitude', sa.Float(), nullable=False, comment='经度'),
            sa.Column('radius', sa.Integer(), nullable=False, server_default='100', comment='打卡范围(米)'),
            sa.Column('is_active', sa.Boolean(), server_default='1', comment='是否启用'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id')
        )
        
        # 添加默认打卡地点
        op.execute("""
            INSERT INTO attendance_locations (name, address, latitude, longitude)
            VALUES ('公司总部', '上海市浦东新区张江高科技园区', 31.203405, 121.604490)
        """)
    else:
        # 如果表存在，检查是否需要添加新列
        existing_columns = {col['name'] for col in inspector.get_columns('attendance_locations')}
        
        if 'radius' not in existing_columns:
            op.add_column('attendance_locations', 
                sa.Column('radius', sa.Integer(), nullable=False, server_default='100', comment='打卡范围(米)'))
        
        if 'is_active' not in existing_columns:
            op.add_column('attendance_locations',
                sa.Column('is_active', sa.Boolean(), server_default='1', comment='是否启用'))
        
        if 'created_at' not in existing_columns:
            op.add_column('attendance_locations',
                sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')))
        
        if 'updated_at' not in existing_columns:
            op.add_column('attendance_locations',
                sa.Column('updated_at', sa.DateTime(), 
                    server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

def downgrade():
    # 由于表可能已经存在且包含数据，这里我们不删除表
    pass
