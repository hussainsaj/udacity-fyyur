"""empty message

Revision ID: 743ae496b1d0
Revises: 20aa3913ca52
Create Date: 2022-07-17 16:46:24.233092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '743ae496b1d0'
down_revision = '20aa3913ca52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('showDate', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'showDate')
    # ### end Alembic commands ###
