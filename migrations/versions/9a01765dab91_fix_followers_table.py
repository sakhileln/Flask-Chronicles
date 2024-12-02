"""fix followers table

Revision ID: 9a01765dab91
Revises: c1ce52d0b690
Create Date: 2024-12-01 23:27:31.888443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a01765dab91'
down_revision = 'c1ce52d0b690'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.alter_column('follower_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.alter_column('follower_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###
