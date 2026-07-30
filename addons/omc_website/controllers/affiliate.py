# -*- coding: utf-8 -*-
import logging

import werkzeug.exceptions

from odoo import http
from odoo.http import request
from odoo.addons.omc_website.models.omc_affiliate import SOURCES

_logger = logging.getLogger(__name__)

VALID_SOURCES = {code for code, _label in SOURCES}


class OmcAffiliateController(http.Controller):

    @http.route(
        "/go/odoo", type="http", auth="public", website=True, sitemap=False,
        methods=["GET"],
    )
    def go_odoo(self, **kwargs):
        """Count the outbound click, then redirect to the affiliate URL.

        Kept out of the sitemap and disallowed in robots.txt: it is a redirect,
        not content. If no URL is configured the link should not be rendered at
        all, so reaching this with an empty parameter is a 404.
        """
        url = request.env["omc.affiliate"].sudo().get_url()
        if not url:
            raise werkzeug.exceptions.NotFound()

        source = kwargs.get("from") or "other"
        if source not in VALID_SOURCES:
            source = "other"

        try:
            request.env["omc.affiliate.click"].sudo().create({
                "source": source,
                "lang": request.env.lang,
            })
        except Exception:  # never block the redirect because of bookkeeping
            _logger.exception("Could not record affiliate click from %s", source)

        return request.redirect(url, local=False)
