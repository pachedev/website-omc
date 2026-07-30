# -*- coding: utf-8 -*-
"""This site has no blog.

`website_blog` is only installed because theme_nextbiz depends on it, so its
public routes are shadowed here: they answer 404 and stay out of the sitemap.
Our module loads after website_blog, so these definitions win.
"""
import werkzeug.exceptions

from odoo import http


class OmcNoBlog(http.Controller):

    @http.route(
        [
            "/blog",
            "/blog/<path:rest>",
            "/blogpost/<path:rest>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def blog_disabled(self, **kwargs):
        raise werkzeug.exceptions.NotFound()
