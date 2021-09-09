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
:mod:`cdi_error` -- Base class for I2B2-CDI exceptions
======================================================

.. module:: cdi_error
    :platform: Linux/Windows
    :synopsis: module contains base class for I2B2-CDI exceptions



"""
# __since__ = "2020-05-08"

class CdiError(Exception):
    """Base class for I2B2-CDI exceptions"""
    pass
