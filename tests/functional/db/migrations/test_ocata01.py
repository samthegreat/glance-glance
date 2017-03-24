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


class TestOcata01Mixin(test_migrations.AlembicMigrationsMixin):

    def _pre_upgrade_ocata01(self, engine):
        images = db_utils.get_table(engine, 'images')
        now = datetime.datetime.now()
        image_members = db_utils.get_table(engine, 'image_members')

        # inserting a public image record
        public_temp = dict(deleted=False,
                           created_at=now,
                           status='active',
                           is_public=True,
                           min_disk=0,
                           min_ram=0,
                           id='public_id')
        images.insert().values(public_temp).execute()

        # inserting a non-public image record for 'shared' visibility test
        shared_temp = dict(deleted=False,
                           created_at=now,
                           status='active',
                           is_public=False,
                           min_disk=0,
                           min_ram=0,
                           id='shared_id')
        images.insert().values(shared_temp).execute()

        # inserting a non-public image records for 'private' visibility test
        private_temp = dict(deleted=False,
                            created_at=now,
                            status='active',
                            is_public=False,
                            min_disk=0,
                            min_ram=0,
                            id='private_id_1')
        images.insert().values(private_temp).execute()
        private_temp = dict(deleted=False,
                            created_at=now,
                            status='active',
                            is_public=False,
                            min_disk=0,
                            min_ram=0,
                            id='private_id_2')
        images.insert().values(private_temp).execute()

        # adding an active as well as a deleted image member for checking
        # 'shared' visibility
        temp = dict(deleted=False,
                    created_at=now,
                    image_id='shared_id',
                    member='fake_member_452',
                    can_share=True,
                    id=45)
        image_members.insert().values(temp).execute()

        temp = dict(deleted=True,
                    created_at=now,
                    image_id='shared_id',
                    member='fake_member_453',
                    can_share=True,
                    id=453)
        image_members.insert().values(temp).execute()

        # adding an image member, but marking it deleted,
        # for testing 'private' visibility
        temp = dict(deleted=True,
                    created_at=now,
                    image_id='private_id_2',
                    member='fake_member_451',
                    can_share=True,
                    id=451)
        image_members.insert().values(temp).execute()

        # adding an active image member for the 'public' image,
        # to test it remains public regardless.
        temp = dict(deleted=False,
                    created_at=now,
                    image_id='public_id',
                    member='fake_member_450',
                    can_share=True,
                    id=450)
        image_members.insert().values(temp).execute()

    def _check_ocata01(self, engine, data):
        # check that after migration, 'visibility' column is introduced
        images = db_utils.get_table(engine, 'images')
        self.assertIn('visibility', images.c)
        self.assertNotIn('is_public', images.c)

        # tests to identify the visibilities of images created above
        rows = images.select().where(
            images.c.id == 'public_id').execute().fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual('public', rows[0][16])

        rows = images.select().where(
            images.c.id == 'shared_id').execute().fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual('shared', rows[0][16])

        rows = images.select().where(
            images.c.id == 'private_id_1').execute().fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual('private', rows[0][16])

        rows = images.select().where(
            images.c.id == 'private_id_2').execute().fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual('private', rows[0][16])


class TestOcata01MySQL(TestOcata01Mixin, test_base.MySQLOpportunisticTestCase):
    pass


class TestOcata01PostgresSQL(TestOcata01Mixin,
                             test_base.PostgreSQLOpportunisticTestCase):
    pass


class TestOcata01Sqlite(TestOcata01Mixin, test_base.DbTestCase):
    pass
