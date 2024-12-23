"""add attendance location model

Revision ID: 07f77f7323f7
Revises: 8264af1f97fb
Create Date: 2024-12-18 09:40:00.030893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07f77f7323f7'
down_revision = '8264af1f97fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attendance_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False, comment='地点名称'),
    sa.Column('address', sa.String(length=200), nullable=False, comment='详细地址'),
    sa.Column('latitude', sa.Float(), nullable=False, comment='纬度'),
    sa.Column('longitude', sa.Float(), nullable=False, comment='经度'),
    sa.Column('radius', sa.Integer(), nullable=True, comment='打卡范围(米)'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否启用'),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key('fk_department_manager', 'departments', 'employees', ['manager_id'], ['id'], use_alter=True)
    op.create_foreign_key('fk_department_parent', 'departments', 'departments', ['parent_id'], ['id'], use_alter=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_department_parent', 'departments', type_='foreignkey')
    op.drop_constraint('fk_department_manager', 'departments', type_='foreignkey')
    op.drop_table('attendance_locations')
    # ### end Alembic commands ###
