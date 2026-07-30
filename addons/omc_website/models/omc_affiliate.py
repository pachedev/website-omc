# -*- coding: utf-8 -*-
from odoo import api, fields, models

PARAM_KEY = "omc_website.odoo_affiliate_url"

# Places on the site that may link out; the controller only accepts these.
SOURCES = [
    ("download", "Download page"),
    ("faq", "FAQ"),
    ("how_it_works", "How it works"),
    ("footer", "Footer"),
    ("other", "Other"),
]


class OmcAffiliate(models.AbstractModel):
    """Odoo affiliate link shown to visitors who do not have Odoo yet.

    The URL lives in the system parameter `omc_website.odoo_affiliate_url`
    (Settings > Technical > System Parameters). Clearing it hides every
    affiliate block on the website at once.
    """

    _name = "omc.affiliate"
    _description = "OMC Odoo Affiliate Link"

    @api.model
    def get_url(self):
        # Read the record instead of get_param: the latter is ormcached, so an
        # edit made in another worker would only show up after a restart.
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .search([("key", "=", PARAM_KEY)], limit=1)
        )
        return (param.value or "").strip()


class OmcAffiliateClick(models.Model):
    """One row per outbound click, to compare how each placement performs.

    Deliberately anonymous: no IP, no user agent, no cookie. The affiliate
    program reports conversions; this only answers "which spot sends clicks".
    """

    _name = "omc.affiliate.click"
    _description = "OMC Affiliate Click"
    _order = "create_date desc"

    name = fields.Char(compute="_compute_name")
    source = fields.Selection(SOURCES, string="Source", required=True, index=True)
    lang = fields.Char(string="Language", index=True)

    @api.depends("source", "create_date")
    def _compute_name(self):
        labels = dict(SOURCES)
        for click in self:
            click.name = labels.get(click.source, click.source or "")
