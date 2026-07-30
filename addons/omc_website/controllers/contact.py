# -*- coding: utf-8 -*-
import logging

from odoo import _, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OmcContactController(http.Controller):
    """Handles the contact form submission.

    Only the POST lives here: /contactus itself is a regular website.page, so
    it stays editable in the website builder. On failure the errors and the
    submitted values travel back through the session and the page redisplays
    them.
    """

    # Declared in the Turnstile widget; Cloudflare echoes it back and
    # `_verify_turnstile_token` rejects tokens minted for another action.
    TURNSTILE_ACTION = "omc_contact"

    def _verify_turnstile(self, token):
        """Server-side check with Odoo's Turnstile helper.

        Without a secret key configured it returns 'no_secret' -> accepted, so
        the form keeps working before Turnstile is set up.
        """
        ip_addr = request.httprequest.remote_addr
        result = (
            request.env["ir.http"]
            .sudo()
            ._verify_turnstile_token(ip_addr, token, self.TURNSTILE_ACTION)
        )
        if result not in ("is_human", "no_secret"):
            _logger.warning("Turnstile rejected a contact submission: %s", result)
        return result in ("is_human", "no_secret")

    def _back_with_errors(self, errors):
        """Re-render the contact page with the errors and the typed values.

        The errors travel in `request.params`, which already holds the posted
        values: anonymous sessions are not persisted in Odoo, so a redirect
        would lose them.
        """
        request.params["omc_errors"] = errors
        # By xmlid: request.render resolves external ids, not view keys.
        return request.render("omc_website.view_contact", {})

    @http.route(
        "/contactus/send", type="http", auth="public", website=True,
        methods=["POST"], csrf=True,
    )
    def contact_submit(self, **post):
        name = (post.get("name") or "").strip()
        email = (post.get("email") or "").strip()
        message = (post.get("message") or "").strip()
        consent = post.get("consent") == "on"
        honeypot = (post.get("website_url_hp") or "").strip()

        if honeypot:  # bots fill the hidden field; drop silently
            return request.redirect("/contactus-thank-you")

        errors = {}
        if not name:
            errors["name"] = _("Please tell us your name.")
        if not email or "@" not in email:
            errors["email"] = _("Please enter a valid email address.")
        if not message:
            errors["message"] = _("Please tell us how we can help.")
        if not consent:
            errors["consent"] = _("You need to accept the privacy policy.")

        turnstile_ok = self._verify_turnstile(
            post.get("turnstile_captcha") or post.get("cf-turnstile-response")
        )
        if not turnstile_ok:
            errors["turnstile"] = _("We could not verify that you are human. Please try again.")

        if errors:
            return self._back_with_errors(errors)

        inquiry_type = post.get("inquiry_type")
        if inquiry_type not in ("support", "sales", "other"):
            inquiry_type = "other"

        request.env["omc.contact.lead"].sudo().create(
            {
                "name": name,
                "email": email,
                "company": (post.get("company") or "").strip(),
                "odoo_version": (post.get("odoo_version") or "").strip(),
                "inquiry_type": inquiry_type,
                "message": message,
                "consent": consent,
                "turnstile_passed": turnstile_ok,
            }
        )
        return request.redirect("/contactus-thank-you")
