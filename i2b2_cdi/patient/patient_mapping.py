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
:mod:`patient_mapping` -- Create/Get patient mapping
========================================================

.. module:: patient_mapping
    :platform: Linux/Windows
    :synopsis: module contains method for creating, retriving encounter mapping from i2b2 instance


"""

import os
from pathlib import Path
import csv
from datetime import datetime as DateTime
from i2b2_cdi.log import cdi_logging
from alive_progress import alive_bar, config_handler
from i2b2_cdi.common.utils import *
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource
from dotenv import load_dotenv
from i2b2_cdi.exception.cdi_database_error import CdiDatabaseError

config_handler.set_global(length=50, spinner='triangles2')
logger = cdi_logging.get_logger(__file__)
env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)


class PatientMapping:
    """The class provides the interface for creating patient mapping i.e. (mapping src encounter id to i2b2 generated encounter num)"""

    def __init__(self):
        self.write_batch_size = 100
        self.patient_list = []
        now = DateTime.now()
        self.patient_num = None
        self.import_time = now.strftime('%Y-%m-%d %H:%M:%S')

    def create_patient_mapping(self, mrn_file_path, mrn_file_delimiter):
        """This method creates patient mapping, it checks if mapping already exists

        Args:
            mrn_file_path (:obj:`str`, mandatory): Path to the mrn file.
            mrn_file_delimiter (:obj:`str`, mandatory): Delimiter to be used while reading the file

        """
        logger.info('Creating patient mapping from mrn file : ' + mrn_file_path)
        try:
            # max lines
            max_line = file_len(mrn_file_path)

            # Get max of patient_num
            self.patient_num = self.get_max_patient_num()

            # Get existing patient mapping
            patient_map = get_patient_mapping()

            # Read input csv file
            with open(mrn_file_path, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=mrn_file_delimiter)
                row_number = 0
                header = next(csv_reader)
                with alive_bar(max_line, bar='smooth') as bar:
                    for row in csv_reader:
                        _validation_error = []
                        row_number += 1

                        # Get patient_num if patient already exists
                        patient_num = self.check_if_patient_exists(
                            row, patient_map)

                        # Get next patient_num if it does not exists
                        if patient_num is None:
                            patient_num = self.get_next_patient_num()
                            self.insert_patient_mapping(
                                patient_num, row, header, patient_map)

                        # Print progress
                        bar()
                    # Save remianing patients (if patient list size is less then write_batch_size )
                    self.save_patient_mapping(self.patient_list)
            print('\n')
        except Exception as e:
            raise e

    def insert_patient_mapping(self, patient_num, pt_ids, pt_id_srcs, patient_map):
        """This method writes patient mapping to the database table using pyodbc connection cursor

        Args:
            patient_num (:obj:`str`, mandatory): I2b2 mapped patient id.
            pt_ids (:obj:`str`, mandatory): List of src patient ids from different sources.
            pt_id_srcs (:obj:`str`, mandatory): List of different sources.
            patient_map (:obj:`str`, mandatory): Patient map of existing mapping.
        """
        count = 0
        try:
            for pt_id in pt_ids:
                if pt_id is not '':
                    # Update the map cache
                    patient_map.update({pt_id: patient_num})
                    
                    pt_map_tuple = (
                        pt_id, pt_id_srcs[count], patient_num, 'demo', self.import_time)
                    self.patient_list.append(pt_map_tuple)

                    if len(self.patient_list) == self.write_batch_size:
                        self.save_patient_mapping(self.patient_list)
                        self.patient_list = []
                count += 1
        except Exception as e:
            raise e

    def save_patient_mapping(self, patients):
        """This method saves patient mappings in a database

        Args:
            patients (:obj:`str`, mandatory): List of patient mappings to be inserted in database.

        """
        try:
            if len(patients) is not 0:
                with I2b2demoDataSource() as cursor:
                    tuple_len = len(patients[0])
                    placeholders = ",".join("?" * tuple_len)
                    query = 'INSERT INTO patient_mapping (patient_ide, patient_ide_source, patient_num, project_id, import_date) VALUES (%s)' % placeholders
                    cursor.executemany(query, self.patient_list)
        except Exception:
            raise

    def check_if_patient_exists(self, pt_ids, patient_map):
        """This method checks if patient mapping already exists in a patient_map

        Args:
            pt_ids (:obj:`str`, mandatory): List of src patient ids from different sources.
            patient_map (:obj:`str`, mandatory): Patient map that contains existing mapping.
        """
        patient_num = None
        try:
            for pt_id in pt_ids:
                if pt_id in patient_map:
                    patient_num = patient_map.get(pt_id)
            return patient_num
        except Exception as e:
            raise e

    def get_max_patient_num(self):
        """This method runs the query on patient mapping to get max patient_num.
        """
        patient_num = None
        try:
            with I2b2demoDataSource() as cursor:
                query = 'select COALESCE(max(patient_num), 0) as patient_num from PATIENT_MAPPING'
                cursor.execute(query)
                row = cursor.fetchone()
                patient_num = row[0]
            return patient_num
        except Exception as e:
            raise e

    def get_next_patient_num(self):
        """This method  increments patient num by 1.
        """
        self.patient_num += 1
        return self.patient_num


def create_patient_mapping(mrn_file_path):
    """This methods contains housekeeping needs to be done before de-identifing patient mrn file.

    Args:
        mrn_file_path (:obj:`str`, mandatory): Path to the input mrn csv file.

    """
    logger.info('Creating patient mapping from mrn file : ' + mrn_file_path)
    if os.path.exists(mrn_file_path):
        D = PatientMapping()
        mrn_file_delimiter = str(os.getenv('CSV_DELIMITER'))
        D.create_patient_mapping(mrn_file_path, mrn_file_delimiter)
    else:
        logger.error('File does not exist : ' + mrn_file_path)


def get_patient_mapping():
    """Get patient mapping data from i2b2 instance"""
    patient_map = {}
    try:
        logger.info('Getting data from patient mapping')
        query = 'SELECT patient_ide, patient_num FROM patient_mapping'
        with I2b2demoDataSource() as (cursor):
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                for row in result:
                    patient_map.update({row[0]: row[1]})

        return patient_map
    except Exception as e:
        raise CdiDatabaseError("Couldn't get data: {}".format(str(e)))
