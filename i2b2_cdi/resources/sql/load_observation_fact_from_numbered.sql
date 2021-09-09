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
use i2b2demodata

drop table pat_numbered
create table pat_numbered (id int IDENTITY , patient_num int);
insert into pat_numbered 
select distinct PATIENT_NUM as patient_num from OBSERVATION_FACT_NUMBERED

DECLARE @pt1 INT
DECLARE @pt2 INT
DECLARE @ptMax INT
DECLARE @st NVARCHAR(4000)
DECLARE @st1 NVARCHAR(4000)
DECLARE @ste NVARCHAR(4000)
SET @pt1 = 1 
SET @pt2 = 1 
SET @ptMax= (SELECT COUNT(*) FROM pat_numbered )

WHILE (@pt1 < @ptMax )

BEGIN
    SET @st1='
    insert into dbo.observation_fact
    select
    r.[ENCOUNTER_NUM] as ENCOUNTER_NUM,
    r.[PATIENT_NUM] as PATIENT_NUM ,
    r.[CONCEPT_CD] as  CONCEPT_CD,
    r.[PROVIDER_ID] as PROVIDER_ID,
    r.[START_DATE] as START_DATE,
    r.[MODIFIER_CD] as MODIFIER_CD,
    r.row_num -1 as INSTANCE_NUM,
    r.[VALTYPE_CD] as VALTYPE_CD,
    r.[TVAL_CHAR] as TVAL_CHAR,
    r.[NVAL_NUM] as NVAL_NUM,
    r.[VALUEFLAG_CD] as VALUEFLAG_CD,
    r.[QUANTITY_NUM] as QUANTITY_NUM,
    r.[UNITS_CD] as UNITS_CD ,
    r.[END_DATE] as END_DATE,
    r.[LOCATION_CD] as LOCATION_CD,
    r.[OBSERVATION_BLOB] as OBSERVATION_BLOB,
    r.[CONFIDENCE_NUM] as CONFIDENCE_NUM,
    r.[UPDATE_DATE] as UPDATE_DATE,
    r.[DOWNLOAD_DATE] as DOWNLOAD_DATE,
    r.[IMPORT_DATE] as IMPORT_DATE,
    r.[SOURCESYSTEM_CD] as SOURCESYSTEM_CD,
    r.[UPLOAD_ID] as UPLOAD_ID
    from (
    select  *,ROW_NUMBER() OVER (PARTITION BY [PATIENT_NUM],[CONCEPT_CD],[MODIFIER_CD],[START_DATE],[ENCOUNTER_NUM],[INSTANCE_NUM],[PROVIDER_ID]
    order by [PATIENT_NUM],[CONCEPT_CD],[MODIFIER_CD],[START_DATE],[ENCOUNTER_NUM],[INSTANCE_NUM],[PROVIDER_ID])
    as row_num
    from [OBSERVATION_FACT_NUMBERED]
    where PATIENT_NUM in (
    '
    
    SET @pt2=@pt1+1000
    SET @st='select patient_num from pat_numbered  where id>='+CONVERT(varchar(10), @pt1)  +' and id< '+CONVERT(varchar(10), @pt2)
    
    SET @ste = @st1 + @st + '))r'
    --PRINT @ste

    --to delete rows for transferred patients
    EXECUTE sp_executesql @ste
    SET @pt1=@pt2
END