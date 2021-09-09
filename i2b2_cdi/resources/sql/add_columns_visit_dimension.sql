--
-- This Source Code Form is subject to the terms of the Mozilla Public License, v.
-- 2.0 with a Healthcare Disclaimer.
-- A copy of the Mozilla Public License, v. 2.0 with the Healthcare Disclaimer can
-- be found under the top level directory, named LICENSE.
-- If a copy of the MPL was not distributed with this file, You can obtain one at
-- http://mozilla.org/MPL/2.0/.
-- If a copy of the Healthcare Disclaimer was not distributed with this file, You
-- can obtain one at the project website https://github.com/igia.
--Copyright (C) 2021-2022 Persistent Systems, Inc.
--
use i2b2demodata;

-- added new columns
IF NOT EXISTS (
  SELECT * 
  FROM   INFORMATION_SCHEMA.columns 
  WHERE TABLE_NAME = 'VISIT_DIMENSION' AND COLUMN_NAME = 'ACTIVITY_TYPE_CD'
)
BEGIN
    ALTER TABLE VISIT_DIMENSION ADD ACTIVITY_TYPE_CD VARCHAR(255)
END

IF NOT EXISTS (
  SELECT * 
  FROM   INFORMATION_SCHEMA.columns 
  WHERE TABLE_NAME = 'VISIT_DIMENSION' AND COLUMN_NAME = 'ACTIVITY_STATUS_CD'
)
BEGIN
    ALTER TABLE VISIT_DIMENSION ADD ACTIVITY_STATUS_CD VARCHAR(255)
END

IF NOT EXISTS (
  SELECT * 
  FROM   INFORMATION_SCHEMA.columns 
  WHERE TABLE_NAME = 'VISIT_DIMENSION' AND COLUMN_NAME = 'PROGRAM_CD'
)
BEGIN
    ALTER TABLE VISIT_DIMENSION ADD PROGRAM_CD VARCHAR(255)
END