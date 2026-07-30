# -*- coding: utf-8 -*-
import uuid

from odoo import api, fields, models, release


class InstanceMonitoring(models.Model):
    _name = "pdev.instance.monitoring"
    _description = "Configuración de monitoreo de la instancia"

    name = fields.Char(
        string="Nombre", required=True, default="Monitoreo de la instancia"
    )
    instance_uuid = fields.Char(
        string="UUID de la instancia",
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: str(uuid.uuid4()),
        help="Identificador único de esta instancia, generado al instalar el módulo.",
    )
    api_key = fields.Char(
        string="API Key",
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: str(uuid.uuid4()),
        help="Clave que autentica las peticiones al endpoint de monitoreo.",
    )
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ("api_key_uniq", "unique(api_key)", "La API Key debe ser única."),
        ("instance_uuid_uniq", "unique(instance_uuid)", "El UUID de la instancia debe ser único."),
    ]

    @api.model
    def _get_config(self):
        """Devuelve el registro de configuración singleton."""
        return self.sudo().search([], limit=1)

    def action_regenerate_api_key(self):
        self.ensure_one()
        self.api_key = str(uuid.uuid4())
        return True

    def get_server_info(self):
        """Información de salud/identidad que consume el monitor externo."""
        self.ensure_one()
        return {
            "status": "ok",
            "instance_uuid": self.instance_uuid,
            "database": self.env.cr.dbname,
            "odoo_version": release.version,
            "server_time": fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
