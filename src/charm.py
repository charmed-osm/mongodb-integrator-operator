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
#
# Learn more at: https://juju.is/docs/sdk

"""MongoDB Integrator.

See more: https://charmhub.io/mongodb-integrator
"""

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, StatusBase

logger = logging.getLogger(__name__)


class CharmError(Exception):
    """Charm Error Exception."""

    def __init__(self, message: str, status_class: StatusBase = BlockedStatus) -> None:
        self.message = message
        self.status_class = status_class
        self.status = status_class(message)


class MongodbIntegrator(CharmBase):
    """MongodbIntegrator Kubernetes sidecar charm."""

    def __init__(self, *args):
        super().__init__(*args)
        event_handler_mapping = {
            self.on.config_changed: self._on_config_changed,
            self.on["mongodb"].relation_joined: self._update_mongodb_relation,
        }

        for event, handler in event_handler_mapping.items():
            self.framework.observe(event, handler)

    # ---------------------------------------------------------------------------
    #   Handlers for Charm Events
    # ---------------------------------------------------------------------------

    def _on_config_changed(self, _) -> None:
        """Handler for the config-changed event."""
        try:
            self._validate_config()
            for relation in self.model.relations["mongodb"]:
                relation.data[self.unit]["connection_string"] = self.config["mongodb-uri"]
            self.unit.status = ActiveStatus()
        except CharmError as e:
            logger.debug(e.message)
            self.unit.status = e.status

    def _update_mongodb_relation(self, event) -> None:
        """Handler for the relation-joined event."""
        try:
            self._validate_config()
            event.relation.data[self.unit]["connection_string"] = self.config["mongodb-uri"]
        except CharmError as e:
            logger.debug(e.message)
            self.unit.status = e.status

    # ---------------------------------------------------------------------------
    #   Validation and configuration and more
    # ---------------------------------------------------------------------------

    def _validate_config(self) -> None:
        """Validate charm configuration.

        Raises:
            CharmError: if charm configuration is invalid.
        """
        logger.debug("validating charm config")
        if not self.config.get("mongodb-uri"):
            raise CharmError("missing mongodb-uri config")
        if not self.config["mongodb-uri"].startswith("mongodb://"):
            raise CharmError("invalid mongodb-uri")


if __name__ == "__main__":  # pragma: no cover
    main(MongodbIntegrator)
