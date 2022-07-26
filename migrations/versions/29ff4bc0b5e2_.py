"""empty message

Revision ID: 29ff4bc0b5e2
Revises: 9db428a271d3
Create Date: 2022-07-17 14:19:13.787721

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '29ff4bc0b5e2'
down_revision = '9db428a271d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'showDate')
    op.drop_column('shows', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('showDate', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
