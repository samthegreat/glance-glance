# Copyright 2016 Rackspace
# Copyright 2013 Intel Corporation
#
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

import os
import sys

from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import migration as alembic_migration
from alembic import script as alembic_script
from oslo_db import exception as db_exception
from oslo_db.sqlalchemy import migration as sqla_migration

from glance.db import migration as db_migration
from glance.db.sqlalchemy import api as db_api
from glance.i18n import _


def get_alembic_config(engine=None):
    """Return a valid alembic config object"""
    ini_path = os.path.join(os.path.dirname(__file__), 'alembic.ini')
    config = alembic_config.Config(os.path.abspath(ini_path))
    if engine is None:
        engine = db_api.get_engine()
    config.set_main_option('sqlalchemy.url', str(engine.url))
    return config


def get_current_alembic_heads():
    """Return current heads (if any) from the alembic migration table"""
    engine = db_api.get_engine()
    with engine.connect() as conn:
        context = alembic_migration.MigrationContext.configure(conn)
        heads = context.get_current_heads()
        return heads


def get_current_legacy_head():
    try:
        legacy_head = sqla_migration.db_version(db_api.get_engine(),
                                                db_migration.MIGRATE_REPO_PATH,
                                                db_migration.INIT_VERSION)
    except db_exception.DbMigrationError:
        legacy_head = None
    return legacy_head


def is_database_under_alembic_control():
    if get_current_alembic_heads():
        return True
    return False


def is_database_under_migrate_control():
    if get_current_legacy_head():
        return True
    return False


def place_database_under_alembic_control():
    a_config = get_alembic_config()

    if not is_database_under_migrate_control():
        return

    if not is_database_under_alembic_control():
        print(_("Database is currently not under Alembic's migration "
                "control."))
        head = get_current_legacy_head()
        if head == 42:
            alembic_version = 'liberty'
        elif head == 43:
            alembic_version = 'mitaka01'
        elif head == 44:
            alembic_version = 'mitaka02'
        elif head == 45:
            alembic_version = 'ocata01'
        elif head in range(1, 42):
            print("Legacy head: ", head)
            sys.exit(_("The current database version is not supported any "
                       "more. Please upgrade to Liberty release first."))
        else:
            sys.exit(_("Unable to place database under Alembic's migration "
                       "control. Unknown database state, can't proceed "
                       "further."))

        print(_("Placing database under Alembic's migration control at "
                "revision:"), alembic_version)
        alembic_command.stamp(a_config, alembic_version)


def get_alembic_branch_head(branch):
    """Return head revision name for particular branch"""
    a_config = get_alembic_config()
    script = alembic_script.ScriptDirectory.from_config(a_config)
    return script.revision_map.get_current_head(branch)
