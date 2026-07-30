# -*- coding: utf-8 -*-
import json
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

PARAM_KEY = "omc_website.demo_credentials"

DEFAULTS = {
    "server": "https://demo-omc.pachedev.com",
    "user": "demo",
    "password": "7x8PU_8V65iM",
}


class OmcDemoCredentials(models.AbstractModel):
    """Reads the demo server credentials shown on the download page.

    They live in a single system parameter (Settings > Technical > System
    Parameters, key `omc_website.demo_credentials`) holding a JSON object, so
    they can be changed at any time without touching the module. The seed value
    is loaded with noupdate, so module upgrades never overwrite an edited one.
    """

    _name = "omc.demo.credentials"
    _description = "OMC Demo Credentials"

    @api.model
    def get_credentials(self):
        # Read the record instead of get_param: the latter is ormcached, so an
        # edit made in another worker would only show up after a restart.
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .search([("key", "=", PARAM_KEY)], limit=1)
        )
        raw = param.value
        values = dict(DEFAULTS)
        if raw:
            try:
                stored = json.loads(raw)
            except ValueError:
                _logger.warning(
                    "System parameter %s is not valid JSON; falling back to defaults.",
                    PARAM_KEY,
                )
            else:
                if isinstance(stored, dict):
                    values.update({k: v for k, v in stored.items() if k in DEFAULTS})
        return values
