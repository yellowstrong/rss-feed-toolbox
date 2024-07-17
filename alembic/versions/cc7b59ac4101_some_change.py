"""some_change

Revision ID: cc7b59ac4101
Revises: 58923c7b0cae
Create Date: 2024-07-15 11:47:46.812565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc7b59ac4101'
down_revision: Union[str, None] = '58923c7b0cae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('download_history', schema=None) as batch_op:
        batch_op.drop_column('save_path')
        batch_op.drop_column('torrent_name')

    with op.batch_alter_table('subscribe', schema=None) as batch_op:
        batch_op.drop_column('quality')
        batch_op.drop_column('resolution')
        batch_op.drop_column('team')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscribe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('resolution', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('quality', sa.VARCHAR(), nullable=True))

    with op.batch_alter_table('download_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('torrent_name', sa.VARCHAR(), nullable=False))
        batch_op.add_column(sa.Column('save_path', sa.VARCHAR(), nullable=False))

    # ### end Alembic commands ###
