"""some_change

Revision ID: 58923c7b0cae
Revises: 861e16a8530e
Create Date: 2024-07-12 16:08:15.352945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58923c7b0cae'
down_revision: Union[str, None] = '861e16a8530e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('download_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rss_title', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('rss_guid', sa.String(), nullable=True))
        batch_op.drop_column('torrent_desc')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('download_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('torrent_desc', sa.VARCHAR(), nullable=True))
        batch_op.drop_column('rss_guid')
        batch_op.drop_column('rss_title')

    # ### end Alembic commands ###
