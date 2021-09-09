#
# This Source Code Form is subject to the terms of the Mozilla Public License, v.
# 2.0 with a Healthcare Disclaimer.
# A copy of the Mozilla Public License, v. 2.0 with the Healthcare Disclaimer can
# be found under the top level directory, named LICENSE.
# If a copy of the MPL was not distributed with this file, You can obtain one at
# http://mozilla.org/MPL/2.0/.
# If a copy of the Healthcare Disclaimer was not distributed with this file, You
# can obtain one at the project website https://github.com/igia.
#
# Copyright (C) 2021-2022 Persistent Systems, Inc.
#
"""
:mod:`cdi_database_connections` -- Provide the context manager class to establish the connection to the database
================================================================================================================

.. module:: cdi_database_connections
    :platform: Linux/Windows
    :synopsis: module contains class to connect to the database

"""
# __since__ = "2020-05-07"

from pyodbc import OperationalError, ProgrammingError
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from i2b2_cdi.log import cdi_logging
from i2b2_cdi.exception.cdi_database_error import CdiDatabaseError
from i2b2_cdi.database.database_helper import DataSource

logger = cdi_logging.get_logger(os.path.basename(__name__))
env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)


class I2b2demoDataSource(DataSource):
    """Provided connection to the i2b2demodata database"""
    def __init__(self):
        self.server = str(os.getenv('I2B2_DS_CRC_IP')) + "," + str(os.getenv('I2B2_DS_CRC_PORT'))
        self.database = str(os.getenv('I2B2_DS_CRC_DB'))
        self.username = str(os.getenv('I2B2_DS_CRC_USER'))
        self.password = str(os.getenv('I2B2_DS_CRC_PASS'))
        super().__init__(self.server, self.database, self.username, self.password)

    def check_database_connection(self):
        try:
            provided_timeout = os.getenv('I2B2_DB_TIMEOUT')
            if provided_timeout is None:
                db_timeout = 300
            else:
                db_timeout = int(provided_timeout)

            is_connected = True
            total_time = 0
            logger.info("connecting to database server...")
            while is_connected:
                try:
                    logger.info("connection time: {}".format(total_time))
                    if total_time > db_timeout:
                        raise TimeoutError(
                            "connection to database server taking longer than usual")

                    with I2b2demoDataSource() as cursor:
                        is_connected = False
                        logger.info("Connected \u2714")
                        logger.info(
                            "Total time taken: {} seconds".format(total_time))
                except TimeoutError as e:
                    raise e
                except (OperationalError, ProgrammingError) as e:
                    time.sleep(12)
                    total_time += 12
                    pass
        except Exception as e:
            raise CdiDatabaseError(
                "Couldn't connect to database: {0}".format(
                    str(e)))


class I2b2metaDataSource(DataSource):
    """Provided connection to the i2b2metadata database"""
    def __init__(self):
        self.server = str(os.getenv('I2B2_DS_ONT_IP')) + "," + str(os.getenv('I2B2_DS_ONT_PORT'))
        self.database = str(os.getenv('I2B2_DS_ONT_DB'))
        self.username = str(os.getenv('I2B2_DS_ONT_USER'))
        self.password = str(os.getenv('I2B2_DS_ONT_PASS'))
        super().__init__(self.server, self.database, self.username, self.password)

    def check_database_connection(self):
        pass
