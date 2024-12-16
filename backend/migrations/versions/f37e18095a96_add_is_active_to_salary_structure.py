"""add_is_active_to_salary_structure

Revision ID: f37e18095a96
Revises: 3859c03adcde
Create Date: 2024-12-15 00:24:49.775281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f37e18095a96'
down_revision = '3859c03adcde'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('salary_structures', sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否激活'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('salary_structures', 'is_active')
    # ### end Alembic commands ###
