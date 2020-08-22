"""empty message

Revision ID: e9d7c1747040
Revises: ae08b1a70a1a
Create Date: 2020-08-17 23:48:41.630152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9d7c1747040'
down_revision = 'ae08b1a70a1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('capacitor_ceramic', 'temperature_min')
    op.drop_column('capacitor_ceramic', 'temperature_max')
    op.drop_column('capacitor_electrolytic', 'temperature_min')
    op.drop_column('capacitor_electrolytic', 'temperature_max')
    op.drop_column('capacitor_tantalum', 'temperature_min')
    op.drop_column('capacitor_tantalum', 'temperature_max')
    op.add_column('component', sa.Column('operating_temperature_max', sa.String(length=30), nullable=True))
    op.add_column('component', sa.Column('operating_temperature_min', sa.String(length=30), nullable=True))
    op.drop_column('fuse_pptc', 'temperature_min')
    op.drop_column('fuse_pptc', 'temperature_max')
    op.drop_column('oscillator_oscillator', 'temperature_min')
    op.drop_column('oscillator_oscillator', 'temperature_max')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('oscillator_oscillator', sa.Column('temperature_max', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('oscillator_oscillator', sa.Column('temperature_min', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('fuse_pptc', sa.Column('temperature_max', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('fuse_pptc', sa.Column('temperature_min', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.drop_column('component', 'operating_temperature_min')
    op.drop_column('component', 'operating_temperature_max')
    op.add_column('capacitor_tantalum', sa.Column('temperature_max', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('capacitor_tantalum', sa.Column('temperature_min', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('capacitor_electrolytic', sa.Column('temperature_max', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('capacitor_electrolytic', sa.Column('temperature_min', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('capacitor_ceramic', sa.Column('temperature_max', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    op.add_column('capacitor_ceramic', sa.Column('temperature_min', sa.VARCHAR(length=30, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
    # ### end Alembic commands ###