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
:mod:`cdi_max_error_reached` -- Provides exception classes for max error count reached exceptions
=================================================================================================

.. module:: cdi_max_error_reached
    :platform: Linux/Windows
    :synopsis: module contains exception classes for max error count reached exceptions


"""
# __since__ = "2020-05-08"

from i2b2_cdi.exception.cdi_error import CdiError

class MaxErrorCountReachedError(CdiError):
    """Exception class for max error record count reached exception"""
    
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return '{0}'.format(self.message)
        else:
            return 'MaxErrorCountReachedError has been raised'
