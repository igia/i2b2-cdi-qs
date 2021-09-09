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
:mod:`perform_encounter` -- process and inserts encounters using bcp utility
============================================================================

.. module:: perform_encounter
    :platform: Linux/Windows
    :synopsis: module contains methods for transforming and importing encounters


"""

from pathlib import Path
import traceback
import argparse
import os
from dotenv import load_dotenv
from i2b2_cdi.encounter import deid_encounter as DeidEncounter
from i2b2_cdi.encounter import transform_file as TransformFile
from i2b2_cdi.log import cdi_logging
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource, I2b2metaDataSource
from i2b2_cdi.common.py_bcp import PyBCP
from i2b2_cdi.encounter import delete_encounter as DeleteEncounter
from i2b2_cdi.common.bcolors import BColors

SUCCESS = BColors.OKGREEN + "Completed \u2714" + BColors.ENDC
FAILURE = BColors.FAIL + "Failed \u2716" + BColors.ENDC

env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)
logger = cdi_logging.get_logger(__file__)


def delete_encounters():
    """Delete the encounters from i2b2 instance"""
    step = BColors.HEADER + "Delete encounters" + BColors.ENDC
    logger.info(step)
    try:
        DeleteEncounter.delete_encounters()
        logger.info(SUCCESS)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error(
            'cdi-pipeline-error: (' +
            step +
            '), - ' +
            traceback.format_exc())
        logger.error(FAILURE)
        raise

def delete_encounter_mappings():
    """Delete the encounter mapping from i2b2 instance"""
    step = BColors.HEADER + "Delete encounter mapping" + BColors.ENDC
    logger.info(step)
    try:
        DeleteEncounter.delete_encounter_mapping()
        logger.info(SUCCESS)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error(
            'cdi-pipeline-error: (' +
            step +
            '), - ' +
            traceback.format_exc())
        logger.error(FAILURE)
        raise


def get_argument_parser():
    """Reads the command line arguments and passes to the ArgumentParser

    Returns:
        Namespace: arguments provided on command line while running the script 

    """
    parser = argparse.ArgumentParser(
        description='Import/Delete encounters from i2b2')
    parser.add_argument('-de', '--delete-encounters',
                        action='store_true', help="Delete encounters from i2b2")
    parser.add_argument('-dem', '--delete-encounter-mappings',
                        action='store_true', help="Delete encounter mappings from i2b2")
    parser.add_argument('-ie', '--import-encounters', dest='encounter_file',
                        type=argparse.FileType('r', encoding='UTF-8'), help="Import encounters into i2b2")
    args = parser.parse_args()
    return args


def load_encounters(file_path):
    """Load encounters from the given file to the i2b2 instance using bcp tool.
    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be imported
    """
    deid_file_path = de_identify_encounters(file_path)
    bcp_file_path = convert_csv_to_bcp(deid_file_path)
    bcp_upload(bcp_file_path)


def de_identify_encounters(file_path):
    """DeIdentify the encounters data
    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be deidentified
    Returns:
        str: path to the deidentified file
    """
    step = BColors.HEADER + "De-identify encounters" + BColors.ENDC
    logger.info(step)
    try:
        deid_file_path, error_file_path = DeidEncounter.do_deidentify(
            file_path)
        logger.info(
            "Check error logs of encounter de-identification if any : " + error_file_path)
        logger.info(SUCCESS)
        return deid_file_path
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


def convert_csv_to_bcp(file_path):
    """Transform the deidentified encounters csv file to the bcp file
    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be converted to bcp file
    Returns:
        str: path to the bcp file
    """
    step = BColors.HEADER + "Convert CSV to BCP" + BColors.ENDC
    logger.info(step)
    try:
        bcp_file_path, error_file_path = TransformFile.do_transform(file_path)
        logger.info(
            "Check error logs of csv to bcp conversion if any : " + error_file_path)
        logger.info(SUCCESS)
        return bcp_file_path
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


def bcp_upload(bcp_file_path):
    """Upload the encounters data from bcp file to the i2b2 instance
    Args:
        bcp_file_path (:obj:`str`, mandatory): Path to the bcp file having encounters data
    """
    step = BColors.HEADER + \
        "Upload using bulk copy (BCP)" + BColors.ENDC
    logger.info(step)
    base_dir = str(Path(bcp_file_path).parents[2])
    try:
        _bcp = PyBCP(
            table_name="visit_dimension_temp",
            import_file=bcp_file_path,
            delimiter=str(os.getenv('CSV_DELIMITER')),
            batch_size=10000,
            error_file= base_dir + "/logs/error_bcp_encounters.log")
        # Create visit dimension temp table
        create_table_path = Path('i2b2_cdi/resources/sql') / \
            'create_visit_dimension_temp.sql'
        _bcp.execute_sql(create_table_path)
        _bcp.upload()
        # Add new columns in visit dimension
        add_column_path = Path(
            'i2b2_cdi/resources/sql') / 'add_columns_visit_dimension.sql'
        _bcp.execute_sql(add_column_path)
        # Load encounters from temp to visit dimension
        load_encounter_path = Path(
            'i2b2_cdi/resources/sql') / 'load_visit_dimension_from_temp.sql'
        _bcp.execute_sql(load_encounter_path)
        logger.info(SUCCESS)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


if __name__ == "__main__":
    args = get_argument_parser()

    if args.delete_encounters:
        delete_encounters()
    elif args.delete_encounter_mappings:
        delete_encounter_mappings()
    elif args.encounter_file:
        # Check database connection before load
        demodata_connection = I2b2demoDataSource()
        demodata_connection.check_database_connection()
        load_encounters(args.encounter_file.name)
        args.encounter_file.close()
