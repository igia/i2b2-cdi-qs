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
USE [i2b2demodata];

IF EXISTS (SELECT * FROM sys.objects 
WHERE object_id = OBJECT_ID(N'[dbo].[VISIT_DIMENSION_TEMP]') AND type in (N'U'))
BEGIN 
   DELETE [dbo].[VISIT_DIMENSION_TEMP]
END

IF  NOT EXISTS (SELECT * FROM sys.objects 
WHERE object_id = OBJECT_ID(N'[dbo].[VISIT_DIMENSION_TEMP]') AND type in (N'U'))
BEGIN

    CREATE TABLE [dbo].[VISIT_DIMENSION_TEMP](
        [ENCOUNTER_NUM] [int] NOT NULL,
        [PATIENT_NUM] [int] NOT NULL,
        [ACTIVE_STATUS_CD] [varchar](50) NULL,
        [START_DATE] [datetime] NULL,
        [END_DATE] [datetime] NULL,
        [INOUT_CD] [varchar](50) NULL,
        [LOCATION_CD] [varchar](50) NULL,
        [LOCATION_PATH] [varchar](900) NULL,
        [LENGTH_OF_STAY] [int] NULL,
        [VISIT_BLOB] [varchar](max) NULL,
        [UPDATE_DATE] [datetime] NULL,
        [DOWNLOAD_DATE] [datetime] NULL,
        [IMPORT_DATE] [datetime] NULL,
        [SOURCESYSTEM_CD] [varchar](50) NULL,
        [UPLOAD_ID] [int] NULL,
        [ACTIVITY_TYPE_CD] [varchar](255) NULL,
        [ACTIVITY_STATUS_CD] [varchar](255) NULL,
        [PROGRAM_CD] [varchar](255) NULL
    )
END