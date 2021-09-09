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
WHERE object_id = OBJECT_ID(N'[dbo].[PATIENT_DIMENSION_TEMP]') AND type in (N'U'))
BEGIN 
   DELETE [dbo].[PATIENT_DIMENSION_TEMP]
END

IF  NOT EXISTS (SELECT * FROM sys.objects 
WHERE object_id = OBJECT_ID(N'[dbo].[PATIENT_DIMENSION_TEMP]') AND type in (N'U'))
BEGIN

    CREATE TABLE [dbo].[PATIENT_DIMENSION_TEMP](
        [PATIENT_NUM] [int] NOT NULL,
        [VITAL_STATUS_CD] [varchar](50) NULL,
        [BIRTH_DATE] [datetime] NULL,
        [DEATH_DATE] [datetime] NULL,
        [SEX_CD] [varchar](50) NULL,
        [AGE_IN_YEARS_NUM] [int] NULL,
        [LANGUAGE_CD] [varchar](50) NULL,
        [RACE_CD] [varchar](50) NULL,
        [MARITAL_STATUS_CD] [varchar](50) NULL,
        [RELIGION_CD] [varchar](50) NULL,
        [ZIP_CD] [varchar](10) NULL,
        [STATECITYZIP_PATH] [varchar](700) NULL,
        [INCOME_CD] [varchar](50) NULL,
        [PATIENT_BLOB] [varchar](max) NULL,
        [UPDATE_DATE] [datetime] NULL,
        [DOWNLOAD_DATE] [datetime] NULL,
        [IMPORT_DATE] [datetime] NULL,
        [SOURCESYSTEM_CD] [varchar](50) NULL,
        [UPLOAD_ID] [int] NULL,
    )
END