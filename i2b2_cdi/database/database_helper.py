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
:mod:`database_helper` -- Provide the context manager class to establish the connection to the database
=======================================================================================================

.. module:: database_helper
    :platform: Linux/Windows
    :synopsis: module contains class to connect to the database

"""
# __since__ = "2020-05-08"

import pyodbc
from i2b2_cdi.exception.cdi_database_error import CdiDatabaseError
from i2b2_cdi.log import cdi_logging

logger = cdi_logging.get_logger(__file__)

class DataSource:
    """Provided the database connection and cursor"""
    def __init__(
            self,
            server='',
            database='',
            username='',
            password=''):
        self.server = server #: Database server url
        self.database = database #: Database name
        self.username = username #: Database username
        self.password = password #: Database password
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Create the connection to the database.

        Returns:
            pyodbc.Connection.cursor: Provide the database cursor
            
        """
        try:
            self.connection = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                self.server +
                ';DATABASE=' +
                self.database +
                ';UID=' +
                self.username +
                ';PWD=' +
                self.password)
            self.cursor = self.connection.cursor()
            return self.cursor
        except Exception as e:
            raise

    def __exit__(self, type, value, traceback):
        """Close the database connection and cursor and also logs errors if any

        Args:
            type (:obj:`type`, mandatory): Type of the exception
            value (:obj:`value`, mandatory): Value of the exception
            traceback (:obj:`traceback`, mandatory): traceback of the exception
            
        """
        if type:
            self.connection.rollback()
            logger.error('Type: ', type)
            logger.error('Value: ', value)
            logger.error('Traceback: ', traceback)
        else:
            self.connection.commit()

        self.cursor.close()
        self.connection.close()

    def check_database_connection(self):
        """Check whether the database conection is live or not"""
        pass
