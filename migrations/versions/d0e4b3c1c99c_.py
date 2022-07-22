"""empty message

Revision ID: d0e4b3c1c99c
Revises: 3b93d7c56d41
Create Date: 2022-07-17 10:27:23.969586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0e4b3c1c99c'
down_revision = '3b93d7c56d41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('artists', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('artists', sa.Column('city_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'artists', 'cities', ['city_id'], ['id'])
    op.drop_column('artists', 'city')
    op.drop_column('artists', 'state')
    op.add_column('venue-genres', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.drop_constraint('venue-genres_artist_id_fkey', 'venue-genres', type_='foreignkey')
    op.create_foreign_key(None, 'venue-genres', 'venues', ['venue_id'], ['id'])
    op.drop_column('venue-genres', 'artist_id')
    op.add_column('venues', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('city_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'venues', 'cities', ['city_id'], ['id'])
    op.drop_column('venues', 'city')
    op.drop_column('venues', 'state')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('venues', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'venues', type_='foreignkey')
    op.drop_column('venues', 'city_id')
    op.drop_column('venues', 'seeking_description')
    op.drop_column('venues', 'seeking_talent')
    op.drop_column('venues', 'website_link')
    op.add_column('venue-genres', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'venue-genres', type_='foreignkey')
    op.create_foreign_key('venue-genres_artist_id_fkey', 'venue-genres', 'artists', ['artist_id'], ['id'])
    op.drop_column('venue-genres', 'venue_id')
    op.add_column('artists', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('artists', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'artists', type_='foreignkey')
    op.drop_column('artists', 'city_id')
    op.drop_column('artists', 'seeking_description')
    op.drop_column('artists', 'seeking_venue')
    # ### end Alembic commands ###