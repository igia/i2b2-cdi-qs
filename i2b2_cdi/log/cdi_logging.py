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
:mod:`cdi_logging` -- provide the logger
========================================

.. module:: cdi_logging
    :platform: Linux/Windows
    :synopsis: module contains method for initializing the logger

=======

"""

import logging
import sys
import logstash
import os



def get_logger(logger_name):
    """Provide the logger instance which has been configured to print logs of different log levels and streams the logs to the Kibana as well as to the console

    Args:
        logger_name (str): name of the resource to which the loggers need to be added

    Returns:
        Logger: logger for the provided resource

    """
    host = 'localhost'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # logger handler for printing logs on kibana
    logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))

    # logger handler for printing logs on console/terminal
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def format_error_log(message='', error=None):
    """Format the logger message

    Args:
        message (str): message to be logged
        error (Error): instance of thrown/catched error/exception
    
    Returns:
        str: formatted message to be logged

    """
    if error:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        error_message = template.format(type(error).__name__, error.args)
        return message + " : " + error_message
    else:
        return message
