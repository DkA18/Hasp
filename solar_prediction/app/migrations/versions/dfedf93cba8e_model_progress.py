"""model progress

Revision ID: dfedf93cba8e
Revises: 56c1224be816
Create Date: 2025-02-19 08:31:40.703013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfedf93cba8e'
down_revision = '56c1224be816'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('model_json', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress', sa.JSON(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('model_json', schema=None) as batch_op:
        batch_op.drop_column('progress')

    # ### end Alembic commands ###
