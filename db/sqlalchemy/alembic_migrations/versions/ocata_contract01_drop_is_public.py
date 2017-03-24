#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""remove is_public from images

Revision ID: ocata_contract01
Revises: mitaka02
Create Date: 2017-01-27 12:58:16.647499

"""

from alembic import op
from sqlalchemy import MetaData, Table

from glance.db import migration

# revision identifiers, used by Alembic.
revision = 'ocata_contract01'
down_revision = 'mitaka02'
branch_labels = migration.CONTRACT_BRANCH
depends_on = 'expand'


MYSQL_DROP_INSERT_TRIGGER = """
DROP TRIGGER insert_visibility;
"""

MYSQL_DROP_UPDATE_TRIGGER = """
DROP TRIGGER update_visibility;
"""


def _drop_column():
    op.drop_index('ix_images_is_public', 'images')
    op.drop_column('images', 'is_public')


def _drop_triggers(engine):
    engine_name = engine.engine.name
    if engine_name == "mysql":
        op.execute(MYSQL_DROP_INSERT_TRIGGER)
        op.execute(MYSQL_DROP_UPDATE_TRIGGER)


def _set_nullability_and_default_on_visibility(meta):
    # NOTE(hemanthm): setting the default on 'visibility' column
    # to 'shared'. Also, marking it as non-nullable.
    images = Table('images', meta, autoload=True)
    images.c.visibility.alter(nullable=False, server_default='shared')


def upgrade():
    migrate_engine = op.get_bind()
    meta = MetaData(bind=migrate_engine)

    _drop_column()
    _drop_triggers(migrate_engine)
    _set_nullability_and_default_on_visibility(meta)
