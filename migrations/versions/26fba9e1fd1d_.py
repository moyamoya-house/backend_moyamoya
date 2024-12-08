"""empty message

Revision ID: 26fba9e1fd1d
Revises: 770ee2f96cc1
Create Date: 2024-12-06 22:42:40.102043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26fba9e1fd1d'
down_revision = '770ee2f96cc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_read', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_column('is_read')

    # ### end Alembic commands ###