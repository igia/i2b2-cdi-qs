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
:mod:`perform_patient` -- process patient mapping
=================================================

.. module:: perform_patient
    :platform: Linux/Windows
    :synopsis: module contains methods for importing, deleting patient mappings


"""

from pathlib import Path
import traceback
import argparse
import os
from dotenv import load_dotenv
from i2b2_cdi.log import cdi_logging
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource, I2b2metaDataSource
from i2b2_cdi.patient import delete_patient
from i2b2_cdi.patient import patient_mapping
from i2b2_cdi.patient import transform_file as TransformFile
from i2b2_cdi.patient import deid_patient as DeidPatient
from i2b2_cdi.common.py_bcp import PyBCP
from i2b2_cdi.common.bcolors import BColors

SUCCESS = BColors.OKGREEN + "Completed \u2714" + BColors.ENDC
FAILURE = BColors.FAIL + "Failed \u2716" + BColors.ENDC

env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)
logger = cdi_logging.get_logger(__file__)


def get_argument_parser():
    """Reads the command line arguments and passes to the ArgumentParser

    Returns:
        Namespace: arguments provided on command line while running the script 

    """
    parser = argparse.ArgumentParser(
        description='Import/Delete patient mapping from i2b2')
    parser.add_argument('-dpm', '--delete-patient-mappings',
                        action='store_true', help="Delete patient mappings from i2b2")
    parser.add_argument('-ipm', '--import-patient-mappings', dest='mrn_file', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import patient mapping into i2b2")
    parser.add_argument('-dp', '--delete-patients',
                        action='store_true', help="Delete patients from i2b2")
    parser.add_argument('-ip', '--import-patients', dest='patient_file', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import patients into i2b2")
    args = parser.parse_args()
    return args


def delete_patient_mappings():
    """Delete patient mapping from i2b2 instance"""
    step = BColors.HEADER + "Delete patient mapping" + BColors.ENDC
    logger.info(step)
    try:
        delete_patient.delete_patient_mapping_i2b2_demodata()
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


def delete_patients():
    """Delete patients from i2b2 instance"""
    step = BColors.HEADER + "Delete patients" + BColors.ENDC
    logger.info(step)
    try:
        delete_patient.delete_patients_i2b2_demodata()
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


def load_patient_mapping(mrn_file_path):
    """Load patient mapping from the given mrn file to the i2b2 instance using pyodbc.

    Args:
        mrn_file_path (:obj:`str`, mandatory): Path to the file which needs to be imported
    """
    step = BColors.HEADER + "Import patient mapping" + BColors.ENDC
    logger.info(step)
    try:
        patient_mapping.create_patient_mapping(mrn_file_path)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error(
            'cdi-pipeline-error: (' +
            step +
            '), - ' +
            traceback.format_exc())
        logger.error(FAILURE)
        raise


def load_patients(patient_file_path):
    """Load patients from the given patient file to the i2b2 instance using pyodbc.

    Args:
        patient_file_path (:obj:`str`, mandatory): Path to the file which needs to be imported
    """
    deid_file_path = de_identify_patients(patient_file_path)
    bcp_file_path = convert_csv_to_bcp(deid_file_path)
    bcp_upload(bcp_file_path)


def de_identify_patients(file_path):
    """DeIdentify the patients data

    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be deidentified

    Returns:
        str: path to the deidentified file
    """
    step = BColors.HEADER + "De-identify patients" + BColors.ENDC
    logger.info(step)
    try:
        deid_file_path, error_file_path = DeidPatient.do_deidentify(file_path)
        logger.info(
            "Check error logs of patients de-identification if any : " + error_file_path)
        logger.info(SUCCESS)
        return deid_file_path
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


def convert_csv_to_bcp(file_path):
    """Transform the de-dentified patients csv file to the bcp file

    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be converted to bcp file

    Returns:
        str: path to the bcp file
    """
    step = BColors.HEADER + "Convert CSV to BCP" + BColors.ENDC
    logger.info(step)
    try:
        bcp_file_path = TransformFile.do_transform(file_path)
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
            table_name="patient_dimension_temp",
            import_file=bcp_file_path,
            delimiter=str(os.getenv('CSV_DELIMITER')),
            batch_size=10000,
            error_file=base_dir + "/logs/error_bcp_patients.log")
        create_table_path = Path('i2b2_cdi/resources/sql') / \
            'create_patient_dimension_temp.sql'
        _bcp.execute_sql(create_table_path)
        _bcp.upload()
        load_patient_path = Path('i2b2_cdi/resources/sql') / \
            'load_patient_dimension_from_temp.sql'
        _bcp.execute_sql(load_patient_path)
        logger.info(SUCCESS)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


if __name__ == "__main__":
    args = get_argument_parser()

    if args.delete_patient_mappings:
        delete_patient_mappings()
    if args.delete_patients:
        delete_patients()
    elif args.mrn_file:
        # Check database connection before load
        demodata_connection = I2b2demoDataSource()
        demodata_connection.check_database_connection()
        load_patient_mapping(args.mrn_file.name)
        args.mrn_file.close()
    elif args.patient_file:
        # Check database connection before load
        demodata_connection = I2b2demoDataSource()
        demodata_connection.check_database_connection()
        load_patients(args.patient_file.name)
        args.patient_file.close()
