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

import datetime

from oslo_db.sqlalchemy import test_base
from oslo_db.sqlalchemy import utils as db_utils

from glance.tests.functional.db import test_migrations


class TestMitaka02Mixin(test_migrations.AlembicMigrationsMixin):

    def _pre_upgrade_mitaka02(self, engine):
        metadef_resource_types = db_utils.get_table(engine,
                                                    'metadef_resource_types')
        now = datetime.datetime.now()
        db_rec1 = dict(id='9580',
                       name='OS::Nova::Instance',
                       protected=False,
                       created_at=now,
                       updated_at=now,)
        db_rec2 = dict(id='9581',
                       name='OS::Nova::Blah',
                       protected=False,
                       created_at=now,
                       updated_at=now,)
        db_values = (db_rec1, db_rec2)
        metadef_resource_types.insert().values(db_values).execute()

    def _check_mitaka02(self, engine, data):
        metadef_resource_types = db_utils.get_table(engine,
                                                    'metadef_resource_types')
        result = (metadef_resource_types.select()
                  .where(metadef_resource_types.c.name == 'OS::Nova::Instance')
                  .execute().fetchall())
        self.assertEqual(0, len(result))

        result = (metadef_resource_types.select()
                  .where(metadef_resource_types.c.name == 'OS::Nova::Server')
                  .execute().fetchall())
        self.assertEqual(1, len(result))


class TestMitaka02MySQL(TestMitaka02Mixin,
                        test_base.MySQLOpportunisticTestCase):
    pass


class TestMitaka02PostgresSQL(TestMitaka02Mixin,
                              test_base.PostgreSQLOpportunisticTestCase):
    pass


class TestMitaka02Sqlite(TestMitaka02Mixin, test_base.DbTestCase):
    pass
