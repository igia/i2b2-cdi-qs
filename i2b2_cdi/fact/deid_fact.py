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
:mod:`deid_fact` -- De-identifying facts
========================================

.. module:: deid_fact
    :platform: Linux/Windows
    :synopsis: module contains methods for mappping src_patient_id with i2b2 generated patient_num.


"""

from dateformat import DateFormat
import os
from pathlib import Path
import csv
from datetime import datetime as DateTime
from i2b2_cdi.exception.cdi_max_err_reached import MaxErrorCountReachedError
from i2b2_cdi.log import cdi_logging
from alive_progress import alive_bar, config_handler
from i2b2_cdi.common.utils import *
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource
from i2b2_cdi.patient import patient_mapping as PatientMapping
from i2b2_cdi.encounter import encounter_mapping as EncounterMapping
from dotenv import load_dotenv

config_handler.set_global(length=50, spinner='triangles2')
logger = cdi_logging.get_logger(__file__)
env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)


class DeidFact:
    """The class provides the interface for de-identifying i.e. (mapping src patient id to i2b2 generated patient num) observation fact file"""

    def __init__(self):
        self.date_format = DateFormat("YYYY-MM-DD hh:mm:ss")
        self.err_records_max = int(os.getenv('MAX_VALIDATION_ERROR_COUNT'))
        self.write_batch_size = 100
        now = DateTime.now()
        self.import_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.deid_header = ['EncounterID', 'PatientID', 'ConceptCD', 'ProviderID',
                            'StartDate', 'ModifierCD', 'InstanceNum', 'value', 'UnitCD']
        self.error_file_header = ['EncounterID', 'PatientID', 'ConceptCD', 'ProviderID', 'StartDate',
                                  'ModifierCD', 'InstanceNum', 'value', 'UnitCD', 'ValidationError', 'ErrorRowNumber']

    def deidentify_fact(self, patient_map, encounter_map, obs_file_path, input_csv_delimiter, deid_file_path, output_deid_delimiter, error_file_path):
        """This method de-identifies csv file and error records will be logged to log file

        Args:
            patient_map (:obj:`str`, mandatory): Patient map for de-identification.
            encounter_map (:obj:`str`, mandatory): Encounter map for de-identification.
            obs_file_path (:obj:`str`, mandatory): Path to the input csv file which needs to be de-identified
            input_csv_delimiter (:obj:`str`, mandatory): Delimiter of the input csv file, which will be used while reading csv file.
            deid_file_path (:obj:`str`, mandatory): Path to the de-identified output file.
            output_deid_delimiter (:obj:`str`, mandatory): Delimiter of the output file, which will be used while writing deid file.
            error_file_path (:obj:`str`, mandatory): Path to the error file, which contains error records

        """

        _error_rows_arr = []
        _valid_rows_arr = []
        max_line = file_len(obs_file_path)
        logger.info('De-identifing observation fact file : ' + obs_file_path)
        try:
            # Write file header
            self.write_deid_file_header(deid_file_path, output_deid_delimiter)
            self.write_error_file_header(error_file_path)
            print('\n')

            # Read input csv file
            with open(obs_file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(
                    csv_file, delimiter=input_csv_delimiter)
                row_number = 0
                with alive_bar(max_line, bar='smooth') as bar:
                    for row in csv_reader:
                        _validation_error = []
                        row_number += 1

                        # Validate record
                        if not row['PatientID']:
                            _validation_error.append("PatientID is Null")
                        if not row['ConceptCD']:
                            _validation_error.append("ConceptCD is Null")
                        if not row['ProviderID']:
                            row['ProviderID'] = 0
                        if row['StartDate'] and not self.is_valid_date_format(row['StartDate']):
                            _validation_error.append(
                                "Invalid start date format")
                        if not row['ModifierCD']:
                            row['ModifierCD'] = '@'
                        if not row['InstanceNum']:
                            row['InstanceNum'] = 1

                        # Replace src patient id by i2b2 patient num
                        patient_num = patient_map.get(row['PatientID'])
                        if patient_num is None:
                            _validation_error.append(
                                "Patient mapping not found")
                        else:
                            row['PatientID'] = patient_num

                        # Replace src encounter id by i2b2 encounter num
                        if row['EncounterID']:
                            encounter_num = encounter_map.get(row['EncounterID'])
                            if encounter_num is None:
                                _validation_error.append("Encounter mapping not found")
                            else:
                                row['EncounterID'] = encounter_num
                        else:
                            row['EncounterID'] = 0

                        # Append error record if found
                        if _validation_error:
                            row['ValidationError'] = ','.join(
                                _validation_error)
                            row['ErrorRowNumber'] = str(row_number)
                            _error_rows_arr.append(row)
                        else:
                            _valid_rows_arr.append(row)

                        # Exit processing, if max error records limit reached.
                        if len(_error_rows_arr) > self.err_records_max:
                            self.write_to_error_file(
                                error_file_path, _error_rows_arr)
                            logger.error(
                                'Exiting observation fact de-identifying as max errors records limit reached - ' + str(self.err_records_max))
                            raise MaxErrorCountReachedError(
                                "Exiting function as max errors records limit reached - " + str(self.err_records_max))

                        # Write valid records to file, if batch size reached.
                        if len(_valid_rows_arr) == self.write_batch_size:
                            self.write_to_deid_file(
                                _valid_rows_arr, deid_file_path, output_deid_delimiter)
                            _valid_rows_arr = []

                        # Print progress
                        bar()

                # Writer valid records to file (remaining records when given batch size does not meet)
                self.write_to_deid_file(
                    _valid_rows_arr, deid_file_path, output_deid_delimiter)

                # Write error records to file
                self.write_to_error_file(error_file_path, _error_rows_arr)
            print('\n')
        except MaxErrorCountReachedError:
            raise
        except Exception as e:
            raise e

    def is_valid_date_format(self, _date):
        """This method checks for date format

        Args:
            _date (:obj:`str`, mandatory): Date to be parsed

        Returns:
            boolean: True if date format is correct else false.
        """
        try:
            self.date_format.parse(_date)
            return True
        except ValueError:
            return False

    def write_deid_file_header(self, deid_file_path, output_deid_delimiter):
        """This method writes the header of deid file using csv writer

        Args:
            deid_file_path (:obj:`str`, mandatory): Path to the deid file.

        """
        try:
            with open(deid_file_path, 'a+') as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=self.deid_header, delimiter=output_deid_delimiter, lineterminator='\n')
                writer.writeheader()
        except Exception as e:
            raise e

    def write_to_deid_file(self, _valid_rows_arr, deid_file_path, output_deid_delimiter):
        """This method writes the list of rows to the deid file using csv writer

        Args:
            _valid_rows_arr (:obj:`str`, mandatory): List of valid facts to be written into deid file.
            deid_file_path (:obj:`str`, mandatory): Path to the output deid file.
            output_deid_delimiter (:obj:`str`, mandatory): Delimeter to be used in deid file.

        """
        try:
            with open(deid_file_path, 'a+') as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=self.deid_header, delimiter=output_deid_delimiter, lineterminator='\n')
                writer.writerows(_valid_rows_arr)
        except Exception as e:
            raise e

    def write_error_file_header(self, deid_file_path):
        """This method writes the header of error file using csv writer

        Args:
            deid_file_path (:obj:`str`, mandatory): Path to the error file.

        """
        try:
            with open(deid_file_path, 'a+') as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=self.error_file_header, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writeheader()
        except Exception as e:
            raise e

    def write_to_error_file(self, error_file_path, _error_rows_arr):
        """This method writes the list of rows to the error file using csv writer

        Args:
            error_file_path (:obj:`str`, mandatory): Path to the error file.
            _error_rows_arr (:obj:`str`, mandatory): List of invalid facts to be written into error file.

        """
        try:
            with open(error_file_path, 'a+') as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=self.error_file_header, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerows(_error_rows_arr)
        except Exception as e:
            raise e


def do_deidentify(obs_file_path):
    """This methods contains housekeeping needs to be done before de-identifing observation fact file.

    Args:
        obs_file_path (:obj:`str`, mandatory): Path to the input observation fact csv file.
    Returns:
        str: Path to de-identified observation fact file
        str: path to the error log file

    """

    if os.path.exists(obs_file_path):
        D = DeidFact()
        deid_file_path = os.path.join(
            Path(obs_file_path).parent, "deid", 'facts.csv')
        error_file_path = os.path.join(
            Path(obs_file_path).parent, "logs", 'error_deid_facts.csv')

        # Delete deid and error file if already exists
        delete_file_if_exists(deid_file_path)
        delete_file_if_exists(error_file_path)

        mkParentDir(deid_file_path)
        mkParentDir(error_file_path)
        input_csv_delimiter = str(os.getenv('CSV_DELIMITER'))
        output_deid_delimiter = str(os.getenv('CSV_DELIMITER'))

        # Get patient mapping and encounter mapping
        patient_map = PatientMapping.get_patient_mapping()
        encounter_map = EncounterMapping.get_encounter_mapping()

        D.deidentify_fact(patient_map, encounter_map, obs_file_path, input_csv_delimiter,
                          deid_file_path, output_deid_delimiter, error_file_path)

        return deid_file_path, error_file_path

    else:
        logger.error('File does not exist : ' + obs_file_path)
