#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: legal@canonical.com
#
# To get in touch with the maintainers, please contact:
# osm-charmers@lists.launchpad.net
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import pytest
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness

from charm import MongodbIntegrator


@pytest.fixture
def harness():
    harness = Harness(MongodbIntegrator)
    harness.begin_with_initial_hooks()
    yield harness
    harness.cleanup()


def test_ready(harness: Harness):
    assert harness.charm.unit.status == BlockedStatus("missing mongodb-uri config")
    harness.update_config({"mongodb-uri": "mongodb://localhost"})
    assert harness.charm.unit.status == ActiveStatus()


def test_mongodb_relation_joined(harness: Harness):
    harness.update_config({"mongodb-uri": "mongodb://localhost"})
    relation_id = harness.add_relation("mongodb", "lcm")
    harness.add_relation_unit(relation_id, "lcm/0")
    relation_data = harness.get_relation_data(relation_id, harness.charm.unit)
    assert harness.charm.unit.status == ActiveStatus()
    assert relation_data == {"connection_string": "mongodb://localhost"}
