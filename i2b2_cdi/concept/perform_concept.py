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
:mod:`perform_concept` -- process concepts
==========================================

.. module:: perform_concept
    :platform: Linux/Windows
    :synopsis: module contains methods for importing, deleting concepts


"""
from pathlib import Path
from shutil import copy, rmtree, make_archive
import traceback
import pysftp
import time
import argparse
import os
from dotenv import load_dotenv
from i2b2_cdi.log import cdi_logging
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource, I2b2metaDataSource
from i2b2_cdi.concept import concept_delete
from i2b2_cdi.common.bcolors import BColors

SUCCESS = BColors.OKGREEN + "Completed \u2714" + BColors.ENDC
FAILURE = BColors.FAIL + "Failed \u2716" + BColors.ENDC

env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)
logger = cdi_logging.get_logger(__file__)

def delete_concepts():
    """Delete the concepts from i2b2 instance"""
    step = BColors.HEADER + "Delete concepts" + BColors.ENDC
    logger.info(step)
    try:
        concept_delete.delete_concepts_i2b2_metadata()
        concept_delete.delete_concepts_i2b2_demodata()
        logger.info(SUCCESS)
    except Exception:
        logger.info(traceback.format_exc())
        logger.error(
            'cdi-pipeline-error: (' +
            step +
            '), - ' +
            traceback.format_exc())
        logger.error(FAILURE)
        raise

def load_concepts(files):
    """Load the concepts from the given zip file to the i2b2 instance.

    Args:
        file_path (:obj:`str`, mandatory): Path to the zip file which needs to be imported
        
    """
    step = BColors.HEADER + "Load concepts" + BColors.ENDC
    logger.info(step)
    time.sleep(1)  # Wait for 10 sec
    try:
        # Create zip structure
        zip_file = create_concept_zip(files)

        logger.info('Uploading zip file to sftp folder ')
        with get_sftp_connection(step) as sftp:
            with sftp.cd('/concept/'):
                sftp.put(zip_file)
        logger.info("Concepts uploaded successfully.")
        
        # Removing zip file after successful upload
        os.remove(zip_file)
        logger.info(SUCCESS)
        print('')
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("ERROR: Failed to load concepts")
        logger.error(
            'cdi-pipeline-error: (' +
            step +
            '), - Failed to load concepts')
        logger.error(FAILURE)
        raise

def create_concept_zip(files):
    """Validates input files. creates missing files. and finally creates the zip file. 

    Args:
        files (:obj:`str`, mandatory): List of input files.
        
    """
    file_map = { 'concepts.csv': False, 'derived_concepts.csv': False, 'concept_mappings.csv': False}
    try:
        logger.info('Validaing csv file names')
        for file in files:
            f = Path(file).name
            value = file_map.get(f)
            if value == False:
                file_map[f] = True
            else:
                raise Exception("Csv file names does not match. Please use correct file names. example : [concepts.csv, derived_concepts.csv, concept_mappings.csv]")
        
        logger.info('Creating zip file')
        proj_dir = 'data/PRJ_01' # Project id
        proj_dir_inner = proj_dir + '/PRJ_01'
        demo_dir = proj_dir_inner + '/DEMO/' # Source system code
        zip_file = proj_dir + '.zip'

        # Create required folder structure
        Path(demo_dir).mkdir(parents=True, exist_ok=True)

        # Create missing files (cdi concept import always needs 3 file)
        for key in file_map:
            if file_map.get(key) == False:
                with open(demo_dir + key, "w") as empty_csv:
                    # empty file
                    pass
    
        # Add multiple files to the zip
        for file in files:
            copy(file, demo_dir)
        
        # Rename file name
        os.rename(demo_dir + 'derived_concepts.csv', demo_dir + 'derived_fact.csv')
        # Create zip
        make_archive(proj_dir, 'zip', proj_dir)

        # Remove folder after zip
        rmtree(proj_dir)
        return zip_file
    except Exception:
        raise

def get_sftp_connection(step):
    """Helps connecting to the SFTP server

    Args:
        step (:obj:`str`, optional): Name of the calling method

    Returns:
        pysftp.Connection: server instance on successfully establishment of connection to the SFTP server 

    """
    sftp_host = str(os.getenv('SFTP_HOST'))
    sftp_port = int(os.getenv('SFTP_PORT'))
    sftp_user = str(os.getenv('SFTP_USER'))
    sftp_pass = str(os.getenv('SFTP_PASS'))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    server = ''
    try:
        server = pysftp.Connection(
            host=sftp_host,
            username=sftp_user,
            password=sftp_pass,
            port=sftp_port,
            cnopts=cnopts)
    except BaseException:
        logger.error("ERROR: Failed to get sftp connection")
        logger.error('cdi-pipeline-error: (' + step +
                     '), - Failed to get sftp connection')
        logger.error(FAILURE)
        raise
    return server

def get_argument_parser():
    """Reads the command line arguments and passes to the ArgumentParser

    Returns:
        Namespace: arguments provided on command line while running the script 

    """
    parser = argparse.ArgumentParser(description='Import/Delete concepts from i2b2')
    parser.add_argument('-dc','--delete-concepts', action='store_true', help="Delete concepts from i2b2")
    parser.add_argument('-ic', '--import-concepts', nargs='+', type=argparse.FileType('r', encoding='UTF-8'), help="Import ontology concepts into i2b2")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_argument_parser()
    if args.delete_concepts:
        delete_concepts()
    elif args.import_concepts:
        files = []
        for file in args.import_concepts:
            files.append(file.name)
        load_concepts(files)
        for file in args.import_concepts:
            file.close()
