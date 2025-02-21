"""some_change

Revision ID: 039088fc7961
Revises: cc7b59ac4101
Create Date: 2024-07-15 14:44:27.513262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '039088fc7961'
down_revision: Union[str, None] = 'cc7b59ac4101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('download_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('torrent_name', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('download_history', schema=None) as batch_op:
        batch_op.drop_column('torrent_name')

    # ### end Alembic commands ###
