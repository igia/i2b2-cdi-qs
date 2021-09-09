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
delete from dbo.observation_fact;
--delete from dbo.concept_dimension;
delete from dbo.patient_dimension;
delete from dbo.provider_dimension;
delete from dbo.visit_dimension;
delete from dbo.patient_mapping;
delete from dbo.encounter_mapping;
