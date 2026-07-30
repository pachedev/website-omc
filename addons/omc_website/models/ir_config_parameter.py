# -*- coding: utf-8 -*-
from odoo import api, models

# Parameters whose value is rendered inside website templates.
WEBSITE_PARAMS = {
    "omc_website.odoo_affiliate_url",
    "omc_website.demo_credentials",
}


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def _clear_website_template_cache(self, keys):
        """Drop the rendered-template cache so edits show up immediately.

        Website templates are cached per process; without this, changing the
        affiliate URL (or the demo credentials) in Settings would only take
        effect after a restart of every worker.
        """
        if keys & WEBSITE_PARAMS:
            self.env.registry.clear_cache("templates")
            self.env.registry.clear_cache()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._clear_website_template_cache({v.get("key") for v in vals_list})
        return records

    def write(self, vals):
        keys = set(self.mapped("key"))
        result = super().write(vals)
        if "key" in vals:
            keys.add(vals["key"])
        self._clear_website_template_cache(keys)
        return result

    def unlink(self):
        keys = set(self.mapped("key"))
        result = super().unlink()
        self._clear_website_template_cache(keys)
        return result
