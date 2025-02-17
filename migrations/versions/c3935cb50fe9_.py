"""empty message

Revision ID: c3935cb50fe9
Revises: 0a5c429ff061
Create Date: 2024-10-22 22:17:19.883099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3935cb50fe9'
down_revision = '0a5c429ff061'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('group_image', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_chat', schema=None) as batch_op:
        batch_op.drop_column('group_image')

    # ### end Alembic commands ###
