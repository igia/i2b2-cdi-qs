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
:mod:`i2b2-loader` -- Perform various operations in data pipeline
=================================================================

.. module:: loader
    :platform: Linux/Windows
    :synopsis: module contains methods for performs various operations in data pipeline

"""
# __since__ = "2020-05-08"

import logging
from pathlib import Path
import logstash
import subprocess
import traceback
import time
import argparse
import os
from dotenv import load_dotenv
from i2b2_cdi.log import cdi_logging
from i2b2_cdi.database.cdi_database_connections import I2b2demoDataSource
from i2b2_cdi.fact import perform_fact
from i2b2_cdi.concept import perform_concept
from i2b2_cdi.patient import perform_patient
from i2b2_cdi.encounter import perform_encounter
from i2b2_cdi.common.bcolors import BColors
from i2b2_cdi.encounter import perform_encounter

SUCCESS = BColors.OKGREEN + "Completed \u2714" + BColors.ENDC
FAILURE = BColors.FAIL + "Failed \u2716" + BColors.ENDC

env_path = Path('i2b2_cdi/resources') / '.env'
load_dotenv(dotenv_path=env_path)
logger = cdi_logging.get_logger(__file__)


def start_i2b2():
    """Starts the docker containers stack of the i2b2 instance"""
    step1 = BColors.HEADER + "Starting i2b2 docker containers" + BColors.ENDC
    logger.info(step1)
    try:
        process = subprocess.Popen(
            ["docker-compose up -d i2b2-web"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True)
        output, errors = process.communicate()
        if output:
            logger.info(output)
            logger.info(SUCCESS)
        else:
            logger.error(errors)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step1 + '):' + str(e))
        logger.error(FAILURE)
        raise


def start_cdi():
    """Starts the docker containers stack of the cdi app"""
    step4 = BColors.HEADER + "Starting cdi docker containers" + BColors.ENDC
    logger.info(step4)
    try:
        process = subprocess.Popen(
            ["docker-compose up -d i2b2-cdi-app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True)
        output, errors = process.communicate()
        if output:
            logger.info(output)
            logger.info(SUCCESS)
        else:
            logger.error(errors)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error('cdi-pipeline-error: (' + step4 + '):' + str(e))
        logger.error(FAILURE)
        raise


def delete_concepts():
    """Delete the concepts. It's wrapper method"""
    perform_concept.delete_concepts()


def delete_facts():
    """Delete the facts. It's wrapper method"""
    perform_fact.delete_facts()


def load_concepts(files):
    """Load the concepts. It's wrapper method

    Args:
        file_path (:obj:`str`, mandatory):

    """
    perform_concept.load_concepts(files)


def load_facts(obs_file_path):
    """Load the facts. It's wrapper method.

    Args:
        file_path (:obj:`str`, mandatory):

    """
    perform_fact.load_facts_using_bcp(obs_file_path)


def delete_encounters():
    """Delete the encounters. It's wrapper method.
    """
    perform_encounter.delete_encounters()


def delete_encounter_mappings():
    """Delete the encounter mapping. It's wrapper method.
    """
    perform_encounter.delete_encounter_mappings()


def load_encounters(file_path):
    """Load the encounters. It's wrapper method.
    Args:
        file_path (:obj:`str`, mandatory): Input encounter file.
    """
    perform_encounter.load_encounters(file_path)


def delete_patient_mappings():
    """Delete patient mapping. It's wrapper method.
    """
    perform_patient.delete_patient_mappings()

def delete_patients():
    """Delete patients. It's wrapper method.
    """
    perform_patient.delete_patients()

def load_patient_mapping(file_path):
    """Load patient mapping. It's wrapper method.
    Args:
        file_path (:obj:`str`, mandatory): Path to the mrn file.
    """
    perform_patient.load_patient_mapping(file_path)

def load_patients(file_path):
    """Load patients. It's wrapper method.
    Args:
        file_path (:obj:`str`, mandatory): Input patient file.
    """
    perform_patient.load_patients(file_path)

def load_data(dir_path):
    """Load the concepts, facts, encounters etc
    Args:
        dir_path (:obj:`str`, mandatory): Path to the directory where files are placed to load.
    """
    mrn_file = 'mrn.csv'
    encounter_file = 'encounters.csv'
    fact_file = 'facts.csv'
    patient_file = 'patients.csv'
    concept_files_map = {'concepts.csv': False,
                         'derived_concepts.csv': False, 'concept_mappings.csv': False}
    data_files_map = {mrn_file: False, encounter_file: False, fact_file: False, patient_file: False}
    # Get all files in a folder
    files = os.listdir(dir_path)
    for file in files:
        if file in concept_files_map:
            concept_files_map[file] = True
    for file in files:
        if file in data_files_map:
            data_files_map[file] = True
    # Import concepts
    concept_files = []
    for file in concept_files_map:
        if concept_files_map.get(file):
            concept_files.append(dir_path + '/' + file)
    if concept_files:
        load_concepts(concept_files)

    # Import facts, encounters, patients and mrns
    if data_files_map.get(mrn_file):
        load_patient_mapping(dir_path + '/' + mrn_file)
    if data_files_map.get(patient_file):
        load_patients(dir_path + '/' + patient_file)
    if data_files_map.get(encounter_file):
        load_encounters(dir_path + '/' + encounter_file)
    if data_files_map.get(fact_file):
        load_facts(dir_path + '/' + fact_file)


def dir_path(dir):
    if os.path.isdir(dir):
        return dir
    else:
        raise argparse.ArgumentTypeError(
            "'{0}' is not a valid directory".format(dir))


def get_argument_parser():
    parser = argparse.ArgumentParser(
        description='Import/Delete data from i2b2')

    parser.add_argument('--start-i2b2', action='store_true',
                        help="Start i2b2 docker containers")
    parser.add_argument('--start-cdi', action='store_true',
                        help="Start cdi docker containers")
    parser.add_argument('-dd', '--delete-data',
                        action='store_true', help="Delete all data from i2b2")
    parser.add_argument('-ld', '--load-data', type=dir_path,
                        help="Load data into i2b2. In this command, file names should be strictly followed. For concepts [concepts.csv', 'derived_concepts.csv', 'concept_mappings.csv'] and for data ['mrn.csv', 'patients.csv', 'encounters.csv', 'facts.csv']")
    parser.add_argument('-dc', '--delete-concepts',
                        action='store_true', help="Delete concepts from i2b2")
    parser.add_argument('-ic', '--import-concepts', nargs='+', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import ontology concepts into i2b2")
    parser.add_argument('-df', '--delete-facts',
                        action='store_true', help="Delete facts from i2b2")
    parser.add_argument('-if', '--import-facts', dest='fact_file', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import observation facts into i2b2")
    parser.add_argument('-dem', '--delete-encounter-mappings',
                        action='store_true', help="Delete encounter mappings from i2b2")
    parser.add_argument('-de', '--delete-encounters',
                        action='store_true', help="Delete encounters from i2b2")
    parser.add_argument('-ie', '--import-encounters', dest='encounter_file',
                        type=argparse.FileType('r', encoding='UTF-8'), help="Import encounters into i2b2")
    parser.add_argument('-dpm', '--delete-patient-mappings',
                        action='store_true', help="Delete patient mappings from i2b2")
    parser.add_argument('-ipm', '--import-patient-mappings', dest='mrn_file', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import patient mappings into i2b2")
    parser.add_argument('-dp', '--delete-patients',
                        action='store_true', help="Delete patients from i2b2")
    parser.add_argument('-ip', '--import-patients', dest='patient_file', type=argparse.FileType(
        'r', encoding='UTF-8'), help="Import patients into i2b2")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_argument_parser()
    if args.start_i2b2:
        start_i2b2()
    elif args.start_cdi:
        start_cdi()
    elif args.delete_data:
        # Cleanup i2b2
        delete_concepts()
        delete_patient_mappings()
        delete_patients()
        delete_encounter_mappings()
        delete_encounters()
        delete_facts()
    elif args.load_data:
        load_data(args.load_data)
    elif args.delete_concepts:
        delete_concepts()
    elif args.delete_facts:
        delete_facts()
    elif args.import_concepts:
        files = []
        for file in args.import_concepts:
            files.append(file.name)
        load_concepts(files)
        for file in args.import_concepts:
            file.close()
    elif args.fact_file:
        # Check database connection before load
        demodata_connection = I2b2demoDataSource()
        demodata_connection.check_database_connection()
        load_facts(args.fact_file.name)
        args.fact_file.close()
    elif args.delete_encounters:
        delete_encounters()
    elif args.delete_encounter_mappings:
        delete_encounter_mappings()
    elif args.encounter_file:
        # Check database connection before load
        demodata_connection = I2b2demoDataSource()
        demodata_connection.check_database_connection()
        load_encounters(args.encounter_file.name)
        args.encounter_file.close()
    elif args.delete_patient_mappings:
        delete_patient_mappings()
    elif args.delete_patients:
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
    
