"""remove "destineo_" in field name for instance

Revision ID: 499761993c22
Revises: 20e7cc528c9e
Create Date: 2015-03-02 16:26:40.696605

"""

# revision identifiers, used by Alembic.
revision = '499761993c22'
down_revision = '20e7cc528c9e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('instance', 'destineo_min_tc_with_car', new_column_name='min_tc_with_car', server_default='300')
    op.alter_column('instance', 'destineo_min_bss', new_column_name='min_bss', server_default='420')
    op.alter_column('instance', 'destineo_min_car', new_column_name='min_car', server_default='300')
    op.alter_column('instance', 'destineo_min_tc_with_bike', new_column_name='min_tc_with_bike', server_default='300')
    op.alter_column('instance', 'destineo_min_tc_with_bss', new_column_name='min_tc_with_bss', server_default='300')
    op.alter_column('instance', 'destineo_min_bike', new_column_name='min_bike', server_default='240')
    op.execute('update instance set min_bike = 240 where min_bike=300')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('instance', 'min_tc_with_car', new_column_name='destineo_min_tc_with_car')
    op.alter_column('instance', 'min_bss', new_column_name='destineo_min_bss')
    op.alter_column('instance', 'min_car', new_column_name='destineo_min_car')
    op.alter_column('instance', 'min_tc_with_bike', new_column_name='destineo_min_tc_with_bike')
    op.alter_column('instance', 'min_tc_with_bss', new_column_name='destineo_min_tc_with_bss')
    op.alter_column('instance', 'min_bike', new_column_name='destineo_min_bike')
    ### end Alembic commands ###
