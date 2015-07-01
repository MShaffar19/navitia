# Copyright (c) 2001-2015, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io
from contextlib import contextmanager
import glob
import os
from navitiacommon import utils, launch_exec
from navitiacommon.launch_exec import launch_exec
import psycopg2
import zipfile
import logging
import time


@contextmanager
def cd(new_dir):
    """
    small helper to change the current dir
    """
    prev_dir = os.getcwd()
    logging.getLogger(__name__).debug("dir = {}, next = {}".format(prev_dir, os.path.expanduser(new_dir)))
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)


def binarize(db_params, output):
    print 'creating data.nav'
    launch_exec('ed2nav',
                ["-o", output,
                 "--connection-string", make_cnx_str(db_params)], logging.getLogger(__name__))


def make_cnx_str(db_params):
    return "host={h} user={u} dbname={dbname} password={pwd}".\
        format(h=db_params.host, u=db_params.user, dbname=db_params.dbname, pwd=db_params.password)


def import_data(data_dir, db_params):
    for f in glob.glob(data_dir + "/*"):
        data_type = utils.type_of_data(f, only_one_file=False)
        if not data_type:
            logging.getLogger(__name__).info('unknown data type for file {}, skipping'.format(f))
            continue

        # Note, we consider that we only have to load one kind of data per directory
        import_component = data_type + '2ed'

        if f.endswith('.zip'):
            # if it's a zip, we unzip it
            zip_file = zipfile.ZipFile(f)
            zip_file.extractall(path=data_dir)

        if data_type in ('fusio', 'gtfs', 'fare'):
            input = data_dir
        else:
            input = f

        launch_exec(import_component,
                    ["-i", input,
                     "--connection-string", make_cnx_str(db_params)], logging.getLogger(__name__))


def load_data(data_dirs, db_params):
    logging.getLogger(__name__).info('loading {}'.format(data_dirs))

    for d in data_dirs:
        import_data(d, db_params)


ALEMBIC_PATH = os.environ.get('ALEMBIC_PATH', '../sql')


def update_db(db_params):
    cnx_string = db_params.cnx_string()

    #we need to enable postgis on the db
    cnx = psycopg2.connect(cnx_string)
    c = cnx.cursor()
    c.execute("create extension postgis;")
    c.close()
    cnx.commit()

    logging.getLogger(__name__).info('message = {}'.format(c.statusmessage))

    with cd(ALEMBIC_PATH):
        res = os.system('PYTHONPATH=. alembic -x dbname="{cnx}" upgrade head'.
                        format(alembic_dir=ALEMBIC_PATH, cnx=cnx_string))

        if res:
            raise Exception('problem with db update')


def generate_nav(data_dir, db_params, output_file):
    if not os.path.exists(data_dir):
        logging.error('impossible to find {}, exiting'.format(data_dir))

    data_dirs = [os.path.join(data_dir, sub_dir_name)
                 for sub_dir_name in os.listdir(data_dir)
                 if os.path.isdir(os.path.join(data_dir, sub_dir_name))]
    if not data_dirs:
        data_dirs = [data_dir]

    update_db(db_params)

    load_data(data_dirs, db_params)

    binarize(db_params, output_file)