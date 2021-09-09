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
:mod:`transform_file` -- Convert csv file to bcp
================================================

.. module:: transform_file
    :platform: Linux/Windows
    :synopsis: module contains methods for transforming data from csv file to bcp file


"""

import math
import csv
import pandas as pd
import sys
import os
from pathlib import Path
from dateformat import DateFormat
from i2b2_cdi.common.utils import *
from datetime import datetime as DateTime
from i2b2_cdi.exception.cdi_max_err_reached import MaxErrorCountReachedError
from i2b2_cdi.exception.cdi_csv_conversion_error import CsvToBcpConversionError
from i2b2_cdi.log import cdi_logging
from alive_progress import alive_bar, config_handler
from dotenv import load_dotenv

config_handler.set_global(length=50, spinner='triangles2')
logger = cdi_logging.get_logger(__file__)

env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)


class TransformFile:
    """The class provides the various methods for transforming csv data to bcp file"""

    def __init__(self):
        self.date_format = DateFormat("YYYY-MM-DD hh:mm:ss")
        self.float_precision_digits = 10
        self.write_batch_size = 100
        self.error_count = 0
        self.error_count_max = 100
        now = DateTime.now()
        self.import_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.bcp_header = ['LINE_NUM', 'EncounterID', 'PatientID', 'ConceptCD', 'ProviderID', 'StartDate', 'ModifierCD', 'InstanceNum', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UnitCD',
                           'END_DATE', 'LOCATION_CD', 'OBSERVATION_BLOB', 'CONFIDENCE_NUM', 'UPDATE_DATE', 'DOWNLOAD_DATE', 'IMPORT_DATE', 'SOURCESYSTEM_CD', 'UPLOAD_ID', 'TEXT_SEARCH_INDEX']

    def csv_to_bcp(self, csv_file_path, input_csv_delimiter, bcp_file_path, output_bcp_delimiter):
        """This method transforms csv file to bcp, Error records will be logged to log file

        Args:
            csv_file_path (:obj:`str`, mandatory): Path to the input csv file which needs to be converted to bcp file
            input_csv_delimiter (:obj:`str`, mandatory): Delimiter of the input csv file, which will be used while reading csv file.
            bcp_file_path (:obj:`str`, mandatory): Path to the output bcp file.
            output_bcp_delimiter (:obj:`str`, mandatory): Delimiter of the output bcp file, which will be used while writing bcp file.

        """

        _valid_rows_arr = []
        max_line = file_len(csv_file_path) - 1
        try:
            print('\n')
            # Read input csv file
            with open(csv_file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(
                    csv_file, delimiter=input_csv_delimiter)
                row_number = 0
                with alive_bar(max_line, bar='smooth') as bar:
                    for row in csv_reader:
                        try:
                            row_number += 1
                            nval_num = ''
                            tval_char = ''
                            valtype_cd = 'T'
                            if not pd.isnull(row['value']) and (self.getValType(row['value']) == 'float' or self.getValType(row['value']) == 'nan'):
                                nval_num = row['value'][0:self.float_precision_digits]
                                tval_char = 'E'
                                valtype_cd = 'N'
                            elif pd.isnull(row['value']):
                                nval_num = 'NaN'
                                tval_char = ''
                                valtype_cd = '@'
                            else:
                                nval_num = ''
                                tval_char = row['value']
                                valtype_cd = 'T'
                            row['LINE_NUM'] = row_number
                            row['VALTYPE_CD'] = valtype_cd
                            row['TVAL_CHAR'] = tval_char
                            row['NVAL_NUM'] = nval_num
                            row['IMPORT_DATE'] = self.import_time
                            row['TEXT_SEARCH_INDEX'] = 1
                            row.pop('value', None)
                            _valid_rows_arr.append(row)

                            # Print progress
                            bar()
                        except Exception as e:
                            logger.error(e)
                            self.error_count += 1
                            if self.error_count > self.error_count_max:
                                raise MaxErrorCountReachedError(
                                    "Exiting function as max errors reached :" + self.error_count_max)

                        # Write valid records to file, if batch size reached.
                        if len(_valid_rows_arr) == self.write_batch_size:
                            self.write_to_bcp_file(
                                _valid_rows_arr, bcp_file_path, output_bcp_delimiter)
                            _valid_rows_arr = []

                    # Writer valid records to file (remaining records when given batch size does not meet)
                    self.write_to_bcp_file(
                        _valid_rows_arr, bcp_file_path, output_bcp_delimiter)
        except MaxErrorCountReachedError:
            raise
        except Exception as e:
            raise CsvToBcpConversionError(cdi_logging.format_error_log(
                "Failed to convert csv to bcp file", e))

    def write_to_bcp_file(self, _valid_rows_arr, bcp_file_path, output_bcp_delimiter):
        """This method writes the list of rows to the bcp file using csv writer

        Args:
            _valid_rows_arr (:obj:`str`, mandatory): List of valid facts to be written into bcp file.
            bcp_file_path (:obj:`str`, mandatory): Path to the output bcp file.
            output_bcp_delimiter (:obj:`str`, mandatory): Delimeter to be used in bcp file.

        """
        try:
            with open(bcp_file_path, 'a+') as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=self.bcp_header, delimiter=output_bcp_delimiter, lineterminator='\n')
                writer.writerows(_valid_rows_arr)
        except Exception as e:
            raise e

    def getValType(self, x):
        """Returns the type of value provided

        Args:
            x (type): value/instance 

        Returns:
            type: provide the type of instance/value 

        """
        try:
            if float(x):
                try:
                    if math.isnan(float(x)):
                        return 'nan'
                except BaseException:
                    pass
                return 'float'
        except BaseException:
            return 'str'


def csv_to_bcp(csv_file_path):
    """Convert the csv file to bcp file and provide the path to the bcp file

    Args:
        _file (str): path to the csv file

    Returns:
        str: path to the bcp file

    """
    if os.path.exists(csv_file_path):
        logger.info('converting csv to bcp : ' + csv_file_path)
        T = TransformFile()
        bcp_file_path = os.path.join(
            Path(csv_file_path).parent, "bcp", 'observation_fact.bcp')

        # Delete bcp and error file if already exists
        delete_file_if_exists(bcp_file_path)
        mkParentDir(bcp_file_path)
        input_csv_delimiter = str(os.getenv('CSV_DELIMITER'))
        output_bcp_delimiter = str(os.getenv('CSV_DELIMITER'))
        T.csv_to_bcp(csv_file_path, input_csv_delimiter,
                     bcp_file_path, output_bcp_delimiter)

        return bcp_file_path
    else:
        logger.error('File does not exist : ' + csv_file_path)
