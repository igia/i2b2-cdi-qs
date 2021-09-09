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
delete from dbo.concept_dimension;

--delete derived concept definitions
IF EXISTS(
SELECT * FROM INFORMATION_SCHEMA.TABLES 
           WHERE TABLE_NAME =  'derived_concept_definition')
BEGIN
 delete from [dbo].[derived_concept_definition]
END

--delete derived concept definitions
IF EXISTS(
SELECT * FROM INFORMATION_SCHEMA.TABLES 
           WHERE TABLE_NAME =  'derived_concept_dependency')
BEGIN
 delete from [dbo].[derived_concept_dependency]
END

--delete derived concept definitions
IF EXISTS(
SELECT * FROM INFORMATION_SCHEMA.TABLES 
           WHERE TABLE_NAME =  'derived_concept_job_details')
BEGIN
 delete from [dbo].[derived_concept_job_details]
END
