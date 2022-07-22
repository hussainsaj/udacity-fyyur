"""empty message

Revision ID: 20aa3913ca52
Revises: 29ff4bc0b5e2
Create Date: 2022-07-17 14:19:47.415590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20aa3913ca52'
down_revision = '29ff4bc0b5e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'date')
    # ### end Alembic commands ###
