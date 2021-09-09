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
:mod:`concept_delete` -- Delete the concepts from i2b2 instance
===============================================================

.. module:: concept_delete
    :platform: Linux/Windows
    :synopsis: module contains methods for deleting concepts


"""
# __since__ = "2020-05-08"

import pymssql
import os
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource, I2b2metaDataSource
from i2b2_cdi.exception.cdi_database_error import CdiDatabaseError
from i2b2_cdi.log import cdi_logging


logger = cdi_logging.get_logger(__file__)


def delete_concepts_i2b2_metadata():
    """Delete the metadata for the concepts from i2b2 instance"""
    try:
        logger.info('Deleting data from i2b2 metadata and table_access')
        queries = ['delete from i2b2', 'delete from table_access']

        with I2b2metaDataSource() as cursor:
            delete(cursor, queries)
    except Exception as e:
        raise CdiDatabaseError("Couldn't delete data: {0}".format(str(e)))


def delete_concepts_i2b2_demodata():
    """Delete the concepts from i2b2 instance"""
    try:
        logger.info(
            'Deleting data from i2b2 concept dimension, derived_concept_definition, derived_concept_dependency and derived_concept_job_details')
        queries = [
            "delete from concept_dimension",
            "IF EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'derived_concept_definition') BEGIN delete from derived_concept_definition END",
            "IF EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'derived_concept_dependency') BEGIN delete from derived_concept_dependency END",
            "IF EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'derived_concept_job_details') BEGIN delete from derived_concept_job_details END"]

        with I2b2demoDataSource() as cursor:
            delete(cursor, queries)
    except Exception as e:
        raise CdiDatabaseError("Couldn't delete data: {0}".format(str(e)))


def delete(cursor, queries):
    """Execute the provided query using the database cursor

    Args:
        cursor (:obj:`pyodbc.Connection.cursor`, mandatory): Cursor obtained from the Connection object connected to the database
        queries (:obj:`list of str`, mandatory): List of delete queries to be executed 
        
    """
    try:
        for query in queries:
            cursor.execute(query)
    except Exception as e:
        raise CdiDatabaseError("Couldn't delete data: {}".format(str(e)))
