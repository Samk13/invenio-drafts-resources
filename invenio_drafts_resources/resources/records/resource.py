# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask import g
from flask_resources import CollectionResource
from flask_resources.context import resource_requestctx
from invenio_records_resources.resources import \
    RecordResource as _RecordResource
from invenio_records_resources.resources.records.utils import es_preference

from .errors import api_redirect


class RecordResource(_RecordResource):
    """Draft-aware RecordResource."""

    def create(self):
        """Create an item."""
        data = resource_requestctx.request_content
        item = self.service.create(
            g.identity, data, links_config=self.config.draft_links_config)
        return item.to_dict(), 201


class RecordVersionsResource(CollectionResource):
    """Record versions resource."""

    def __init__(self, service=None, config=None):
        """Constructor."""
        super().__init__(config=config)
        self.service = service

    def search(self):
        """Perform a search over the record's versions.

        GET /records/:pid_value/versions
        """
        identity = g.identity
        hits = self.service.search_versions(
            resource_requestctx.route["pid_value"],
            identity=identity,
            params=resource_requestctx.url_args,
            links_config=self.config.links_config,
            es_preference=es_preference()
        )
        return hits.to_dict(), 200

    def create(self):
        """Create a new version.

        POST /records/:pid_value/versions
        """
        item = self.service.new_version(
            resource_requestctx.route["pid_value"],
            g.identity,
            links_config=self.config.draft_links_config
        )
        return item.to_dict(), 201

    def read(self):
        """Redirect to latest record.

        GET /records/:pid_value/versions/latest
        """
        item = self.service.read_latest(
            resource_requestctx.route["pid_value"],
            g.identity,
            links_config=self.config.links_config
        )
        api_redirect(location=item["links"]["self"])
