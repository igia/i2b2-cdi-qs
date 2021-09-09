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
:mod:`encounter_mapping` -- Create/Get encounter mapping
========================================================

.. module:: encounter_mapping
    :platform: Linux/Windows
    :synopsis: module contains method for creating, retriving encounter mapping from i2b2 instance

"""

import pymssql
import os
import csv
from datetime import datetime as DateTime
from i2b2_cdi.common.utils import *
from i2b2_cdi.patient import patient_mapping as PatientMapping
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource, I2b2metaDataSource
from i2b2_cdi.exception.cdi_database_error import CdiDatabaseError
from i2b2_cdi.log import cdi_logging
from alive_progress import alive_bar, config_handler
from dotenv import load_dotenv

config_handler.set_global(length=50, spinner='triangles2')
logger = cdi_logging.get_logger(__file__)
env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)


class EncounterMapping:
    """The class provides the interface for de-identifying i.e. (mapping src encounter id to i2b2 generated encounter num) encounter file"""

    def __init__(self):
        self.write_batch_size = 100
        self.encounter_list = []
        now = DateTime.now()
        self.encounter_num = None
        self.import_time = now.strftime("%Y-%m-%d %H:%M:%S")

    def create_encounter_mapping(self, csv_file_path, input_csv_delimiter):
        """This method creates encounter mapping, it checks if mapping already exists

        Args:
            csv_file_path (:obj:`str`, mandatory): Path to the encounter file.
            input_csv_delimiter (:obj:`str`, mandatory): Delimiter to be used while reading the file

        """
        logger.info(
            'Creating encounter mapping from input file : ' + csv_file_path)
        try:
            # max lines
            max_line = file_len(csv_file_path)

            # Get max of encounter_num
            self.encounter_num = self.get_max_encounter_num()

            # Get existing encounter mapping
            encounter_map = get_encounter_mapping()

            # Read input csv file
            with open(csv_file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(
                    csv_file, delimiter=input_csv_delimiter)
                row_number = 0
                with alive_bar(max_line, bar='smooth') as bar:
                    for row in csv_reader:
                        row_number += 1

                        # Print progress
                        bar()

                        if not row['EncounterID']:
                            continue
                        if not row['PatientID']:
                            continue

                        # Get encounter_num if encounter already exists
                        encounter_num = self.check_if_encounter_exists(row['EncounterID'], encounter_map)

                        # Get next encounter_num if it does not exists
                        if encounter_num is None:
                            encounter_num = self.get_next_encounter_num()
                            # Update the map cache
                            encounter_map.update( { row['EncounterID'] : encounter_num } )
                            self.insert_encounter_mapping(
                                encounter_num, row['EncounterID'], 'DEMO', row['PatientID'])
                    
                    # Save remianing encounters (if encounter list size is less then write_batch_size )
                    self.save_encounter_mapping(self.encounter_list)
            print('\n')
        except Exception as e:
            raise e

    def insert_encounter_mapping(self, encounter_num, encounter_id, encounter_src, patient_id):
        """This method writes encounter mapping to the database table using pyodbc connection cursor

        Args:
            encounter_num (:obj:`str`, mandatory): I2b2 mapped encounter id.
            encounter_id (:obj:`str`, mandatory): Src encounter id.
            encounter_src (:obj:`str`, mandatory): Encounter source.

        """
        try:
            encounter_map_tuple = (encounter_id, encounter_src, encounter_num, patient_id, 'DEMO', 'DEMO', self.import_time)
            self.encounter_list.append(encounter_map_tuple)

            if len(self.encounter_list) == self.write_batch_size:
                self.save_encounter_mapping(self.encounter_list)
                self.encounter_list = []
        except Exception as e:
            raise e

    def save_encounter_mapping(self, encounters):
        """This method saves encounter mappings in a database

        Args:
            encounters (:obj:`str`, mandatory): List of encounter mappings to be inserted in database.
        """
        try:
            if len(encounters) is not 0:
                with I2b2demoDataSource() as cursor:
                    tuple_len = len(encounters[0])
                    placeholders = ",".join("?" * tuple_len)
                    query = 'INSERT INTO encounter_mapping (encounter_ide, encounter_ide_source, encounter_num, patient_ide, patient_ide_source, project_id, import_date) VALUES (%s)' % placeholders
                    cursor.executemany(query, self.encounter_list)
        except Exception:
            raise

    def check_if_encounter_exists(self, encounter_id, encounter_map):
        """This method checks if encounter mapping already exists in a database

        Args:
            encounter_id (:obj:`str`, mandatory): Src encounter id.
            encounter_map (:obj:`str`, mandatory): Encounter map that contains existing mapping.
        """
        encounter_num = None
        try:
            if encounter_id in encounter_map:
                encounter_num = encounter_map.get(encounter_id)
            return encounter_num
        except Exception as e:
            raise e

    def get_max_encounter_num(self):
        """This method runs the query on encounter mapping to get max encounter_num.
        """
        encounter_num = None
        try:
            with I2b2demoDataSource() as cursor:
                query = 'select COALESCE(max(encounter_num), 0) as encounter_num from ENCOUNTER_MAPPING'
                cursor.execute(query)
                row = cursor.fetchone()
                encounter_num = row[0]
            return encounter_num
        except Exception as e:
            raise e

    def get_next_encounter_num(self):
        """This method  increments encounter num by 1.
        """
        self.encounter_num += 1
        return self.encounter_num


def create_encounter_mapping(csv_file_path):
    """This methods contains housekeeping needs to be done before creating encounter mapping.

    Args:
        csv_file_path (:obj:`str`, mandatory): Path to the input encounter csv file.

    """

    if os.path.exists(csv_file_path):
        D = EncounterMapping()
        input_csv_delimiter = str(os.getenv('CSV_DELIMITER'))
        D.create_encounter_mapping(csv_file_path, input_csv_delimiter)
    else:
        logger.error('File does not exist : ' + csv_file_path)


def get_encounter_mapping():
    """Get encounter mapping data from i2b2 instance"""
    encounter_map = {}
    try:
        logger.info("Getting data from encounter mapping")
        query = 'SELECT encounter_ide, encounter_num FROM encounter_mapping'

        with I2b2demoDataSource() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                for row in result:
                    encounter_map.update({row[0]: row[1]})

        return encounter_map
    except Exception as e:
        raise CdiDatabaseError("Couldn't get data: {0}".format(str(e)))
