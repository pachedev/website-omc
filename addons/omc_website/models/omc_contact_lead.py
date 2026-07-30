# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OmcContactTag(models.Model):
    _name = "omc.contact.tag"
    _description = "Contact Lead Tag"

    name = fields.Char(string="Name", required=True, translate=True)
    color = fields.Integer(string="Color")

    _name_uniq = models.Constraint("unique (name)", "The tag already exists.")


class OmcContactLead(models.Model):
    """Lead captured from the /contactus form."""

    _name = "omc.contact.lead"
    _description = "OMC Contact Lead"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Name", required=True, tracking=True)
    email = fields.Char(string="Email", required=True, tracking=True)
    company = fields.Char(string="Company")
    odoo_version = fields.Char(string="Odoo version")
    inquiry_type = fields.Selection(
        [
            ("support", "Support"),
            ("sales", "Sales"),
            ("other", "Other"),
        ],
        string="Inquiry type",
        default="other",
        tracking=True,
    )
    message = fields.Text(string="Message", required=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("pending", "Pending"),
            ("contacted", "Contacted"),
            ("interested", "Interested"),
            ("customer", "Customer"),
            ("discarded", "Discarded"),
        ],
        string="Status",
        default="new",
        required=True,
        tracking=True,
        group_expand="_group_expand_state",
    )
    tag_ids = fields.Many2many("omc.contact.tag", string="Tags")
    consent = fields.Boolean(string="Privacy consent", readonly=True)
    turnstile_passed = fields.Boolean(string="Turnstile validated", readonly=True)
    # Integer and not Many2one: crm is an optional dependency, so the comodel
    # may not exist in this database.
    crm_lead_id = fields.Integer(string="CRM Lead ID", readonly=True)
    crm_installed = fields.Boolean(compute="_compute_crm_installed")

    @api.model
    def _group_expand_state(self, states, domain):
        return [key for key, _label in self._fields["state"].selection]

    def _compute_crm_installed(self):
        installed = bool(
            self.env["ir.module.module"]
            .sudo()
            .search_count([("name", "=", "crm"), ("state", "=", "installed")])
        )
        for lead in self:
            lead.crm_installed = installed

    def action_convert_to_crm(self):
        """Manual conversion to CRM. Only available when crm is installed."""
        self.ensure_one()
        if not self.crm_installed:
            raise UserError(_("The CRM module is not installed."))
        if self.crm_lead_id:
            raise UserError(_("This lead has already been converted to CRM."))
        crm_lead = self.env["crm.lead"].create(
            {
                "name": _("Web: %s", self.name),
                "contact_name": self.name,
                "email_from": self.email,
                "partner_name": self.company,
                "description": self.message,
            }
        )
        self.write({"crm_lead_id": crm_lead.id})
        self.message_post(body=_("Converted to a CRM lead (ID %s).", crm_lead.id))
        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "res_id": crm_lead.id,
            "view_mode": "form",
        }
