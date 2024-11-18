"""empty message

Revision ID: 770ee2f96cc1
Revises: 188bc1f08c01
Create Date: 2024-11-18 22:12:59.496392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '770ee2f96cc1'
down_revision = '188bc1f08c01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hash_tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('tag_name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('tag_id'),
    sa.UniqueConstraint('tag_name')
    )
    op.create_table('moyamoya_hashtag',
    sa.Column('moyamoya_hashtag_id', sa.Integer(), nullable=False),
    sa.Column('moyamoya_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['moyamoya_id'], ['moyamoya.moyamoya_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['hash_tag.tag_id'], ),
    sa.PrimaryKeyConstraint('moyamoya_hashtag_id')
    )
    with op.batch_alter_table('moyamoya', schema=None) as batch_op:
        batch_op.drop_column('hash_tag')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('moyamoya', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hash_tag', sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    op.drop_table('moyamoya_hashtag')
    op.drop_table('hash_tag')
    # ### end Alembic commands ###
