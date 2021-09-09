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
:mod:`perform_fact` -- process facts
====================================

.. module:: perform_fact
    :platform: Linux/Windows
    :synopsis: module contains methods for importing, deleting facts

"""

from pathlib import Path
import traceback
import argparse
import os
from dotenv import load_dotenv
from i2b2_cdi.fact import deid_fact as DeidFact
from i2b2_cdi.fact import transform_file as TransformFile
from i2b2_cdi.encounter import perform_encounter as PerformEncounter
from i2b2_cdi.log import cdi_logging
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource, I2b2metaDataSource
from i2b2_cdi.common.py_bcp import PyBCP
from i2b2_cdi.fact import delete_fact
from i2b2_cdi.common.bcolors import BColors

SUCCESS = BColors.OKGREEN + "Completed \u2714" + BColors.ENDC
FAILURE = BColors.FAIL + "Failed \u2716" + BColors.ENDC

env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)
logger = cdi_logging.get_logger(__file__)


def delete_facts():
    """Delete the facts from i2b2 instance"""
    step = BColors.HEADER + "Delete facts" + BColors.ENDC
    logger.info(step)
    try:
        delete_fact.delete_facts_i2b2_demodata()
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
        description='Import/Delete data from i2b2')
    parser.add_argument('-df', '--delete-facts',
                        action='store_true', help="Delete facts from i2b2")
    parser.add_argument('-if', '--import-facts', dest='fact_file', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import observation facts into i2b2")
    args = parser.parse_args()
    return args


def load_facts_using_bcp(obs_file_path):
    """Load the facts from the given file to the i2b2 instance using bcp tool.

    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be imported

    """
    deid_file_path = de_identify_facts(obs_file_path)
    bcp_file_path = convert_csv_to_bcp(deid_file_path)
    bcp_upload(bcp_file_path)


def de_identify_facts(obs_file_path):
    """DeIdentify the fact data

    Args:
        file_path (:obj:`str`, mandatory): Path to the file which needs to be deidentified

    Returns:
        str: path to the deidentified file

    """
    step = BColors.HEADER + "De-identify facts" + BColors.ENDC
    logger.info(step)
    try:
        #data_shift_flag = False
        deid_file_path, error_file_path = DeidFact.do_deidentify(obs_file_path)
        logger.info(
            "Check error logs of fact de-identification if any : " + error_file_path)
        logger.info(SUCCESS)
        return deid_file_path
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


def convert_csv_to_bcp(deid_file_path):
    """Transform the cdi fact file to the bcp fact file

    Args:
        deid_file_path (:obj:`str`, mandatory): Path to the deidentified file which needs to be converted to bcp file

    Returns:
        str: path to the bcp file

    """
    step = BColors.HEADER + "Convert CSV to BCP" + BColors.ENDC
    logger.info(step)
    try:
        bcp_file_path = TransformFile.csv_to_bcp(deid_file_path)
        logger.info(SUCCESS)
        return bcp_file_path
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


def bcp_upload(bcp_file_path):
    """Upload the fact data from bcp file to the i2b2 instance

    Args:
        bcp_file_path (:obj:`str`, mandatory): Path to the bcp file having fact data

    """
    step = BColors.HEADER + \
        "Upload using bulk copy (BCP)" + BColors.ENDC
    logger.info(step)
    base_dir = str(Path(bcp_file_path).parents[2])
    try:
        _bcp = PyBCP(
            table_name="observation_fact_numbered",
            import_file=bcp_file_path,
            delimiter=str(os.getenv('CSV_DELIMITER')),
            batch_size=10000,
            error_file= base_dir + "/logs/error_bcp_facts.log")

        create_table_path = Path('i2b2_cdi/resources/sql') / \
            'create_observation_fact_numbered.sql'
        _bcp.execute_sql(create_table_path)
        _bcp.upload()
        load_fact_path = Path('i2b2_cdi/resources/sql') / \
            'load_observation_fact_from_numbered.sql'
        _bcp.execute_sql(load_fact_path)
        logger.info(SUCCESS)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step + '):' + str(e))
        logger.error(FAILURE)
        raise


if __name__ == "__main__":
    args = get_argument_parser()

    if args.delete_facts:
        delete_facts()
    elif args.fact_file:
        # Check database connection before load
        demodata_connection = I2b2demoDataSource()
        demodata_connection.check_database_connection()
        load_facts_using_bcp(args.fact_file.name)
        args.fact_file.close()
