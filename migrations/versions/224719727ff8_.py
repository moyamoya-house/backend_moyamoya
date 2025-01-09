"""empty message

Revision ID: 224719727ff8
Revises: 4387a98516b5
Create Date: 2025-01-09 23:13:48.781000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '224719727ff8'
down_revision = '4387a98516b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pots', schema=None) as batch_op:
        batch_op.add_column(sa.Column('solution', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pots', schema=None) as batch_op:
        batch_op.drop_column('solution')

    # ### end Alembic commands ###
