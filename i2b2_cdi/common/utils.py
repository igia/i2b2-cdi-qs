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
:mod:`Utils` -- Shared utilities to to be used in whole project
===============================================================

.. module:: Utils
    :platform: Linux/Windows
    :synopsis: module contains classes and methods implemented as part of shared utilities which can be used in whole project


"""

import datetime
import hashlib
import base64
import subprocess
import time
import os
import psutil
from pathlib import Path


fact_fields = 'EncounterID,PatientID,ConceptCD,ProviderID,StartDate,ModifierCD,InstanceNum,value,UnitCD'.split(
    ',')
concept_fields = [
    'Path',
    'Key',
    'ColumnDataType',
    'MetadataXml',
    'FactTableColumn',
    'TableName',
    'ColumnName',
    'Operator',
    'Dimcode']


class Time():
    """Class implements various methods to calculate time required to perform certain operation"""

    def __init__(self):
        self.last_time = time.time()

    def timeStep(self):
        """Calculate the time taken by the particular process and displays it"""
        x = time.time()
        process = psutil.Process(os.getpid())
        print("%2.1fG" % ((process.memory_info().rss) /
                          (1024 * 1024 * 1024)), end=" ")  # in bytes
        print("%3.0fs" % ((x - self.last_time)), end=" ")
        self.last_time = x

# Time().timeStep()


def getHash(_txt):
    d = hashlib.md5(_txt.encode('utf8')).digest()
    return base64.b64encode(d).replace(
        ',',
        '#').replace(
        '\\',
        '#').replace(
            r'\/',
            '#').replace(
                '+',
                'P').replace(
                    '=',
                    'E')[
                        0:10].decode(
                            "utf-8",
        "ignore")

# getHash('helloWET')


def path2Code(path):
    arr = path.replace('_', '').split('/')[1:]
    # return 'test'
    return (('/'.join([a[0:5] + "." + a[-5:] if len(a) > 10 else a for a in arr]) + '-' + getHash(path))[-49:]
            )[-5:] .replace(',', '#').replace('\\', '#').replace(r'\/', '#').replace('+', 'P').replace('=', 'E')


def getParents(_path):
    arr = []
    ancestor = ''  # ancestor
    for _c in _path[1:].split('/'):
        ancestor = ancestor + '/' + _c
        arr.append(ancestor)
    return arr


def file_len(fname):
    """Provide the total number of word counts for the specified file
    
    Args:
       fname (str): name or path of the file for which, the word count to be calculated

    Returns:
        int: count of total number of words from the provided file

    """
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


def mkParentDir(filePath):
    if not os.path.exists(filePath):
        return Path(Path(filePath).parent).mkdir(parents=True, exist_ok=True)

def delete_file_if_exists(_file):
    if os.path.exists(_file):
        os.remove(_file)
