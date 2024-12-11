"""empty message

Revision ID: 4387a98516b5
Revises: 26fba9e1fd1d
Create Date: 2024-12-11 21:56:59.542357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4387a98516b5'
down_revision = '26fba9e1fd1d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chats', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(length=255), nullable=True))
        batch_op.alter_column('message',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chats', schema=None) as batch_op:
        batch_op.alter_column('message',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
        batch_op.drop_column('image')

    # ### end Alembic commands ###
