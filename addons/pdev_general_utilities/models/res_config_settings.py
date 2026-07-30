# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class ResConfigSettings(models.TransientModel):
    """Inherits 'res.config.settings' to add fields for customize auth pages (Login, Signup and Reset password)."""
    _inherit = 'res.config.settings'

    login_style = fields.Selection(
        [('left', 'Left'), ('right', 'Right'), ('middle', 'Middle')],
        string="Estilo de inicio de sesión",
        default='middle',
        help="Select login box position",
    )
    credential_border = fields.Selection(
        [('with', 'Tarjeta con borde'), ('without', 'Sin borde')],
        default='without',
        config_parameter='pdev_general_utilities.credential_border',
    )
    credential_element_color = fields.Char(
        string="Colores de la tarjeta",
        help="Color de elementos de la tarjeta (inputs, botones)",
        default='#596773',
        config_parameter='pdev_general_utilities.credential_element_color',
    )
    background = fields.Selection(
        [('image', 'Imagen'), ('color', 'Color'), ('video', 'Video')],
        string="Tipo de fondo",
        default='color',
        help="Tipo de fondo del inicio de sesión",
    )
    color = fields.Char(
        string="Color de fondo",
        help="Color sólido para el fondo",
    )
    credential_opacity = fields.Integer(
        string="Opacidad de la tarjeta",
        help="Opacidad del recuadro de credenciales (0-100)",
        default=70,
        config_parameter='pdev_general_utilities.credential_opacity',
    )
    gradient_top_color = fields.Char(
        string="Color del gradiente superior",
        help="Color del gradiente superior del fondo",
    )
    gradient_top_opacity = fields.Integer(
        string="Opacidad del gradiente superior",
        help="Opacidad del gradiente superior (0-100)",
        default=0,
    )
    gradient_bottom_color = fields.Char(
        string="Color de gradiente inferior",
        help="Color del gradiente inferior del fondo",
    )
    gradient_bottom_opacity = fields.Integer(
        string="Opacidad del gradiente inferior",
        help="Opacidad del gradiente inferior (0-100)",
        default=0,
    )
    video = fields.Char(string="Video de fondo")
    b_image_id = fields.Many2one('web.background.image', string="Imagen de fondo")
    web_remove_powered_by = fields.Boolean(
        string="Eliminar powered by",
        default=True,
        config_parameter='pdev_general_utilities.web_remove_powered_by',
    )
    disable_passkey = fields.Boolean(
        string="Desactivar llave de seguridad",
        default=False,
        config_parameter='pdev_general_utilities.disable_passkey',
    )

    @api.onchange('background')
    def onchange_background(self):
        if self.background == 'image':
            self.color = False
            self.video = False
        elif self.background == 'color':
            self.b_image_id = False
            self.video = False
        elif self.background == 'video':
            self.b_image_id = False
            self.color = False
        else:
            self.b_image_id = self.color = self.video = False

    @api.onchange('video')
    def _check_youtube_url(self):
        youtube_pattern = re.compile(
            r'^(https?://)?(www\.)?'
            r'(youtube\.com/(watch\?v=|embed/)|youtu\.be/)'
            r'[\w-]{11}($|[?&])'
        )
        for record in self:
            if record.video and not youtube_pattern.match(record.video.strip()):
                raise ValidationError(
                    _("Ingresa una URL válida de YouTube (ejemplo: https://youtu.be/xxxxxx).")
                )

    @api.onchange('gradient_top_opacity', 'gradient_bottom_opacity', 'credential_opacity')
    def _check_opacity(self):
        for record in self:
            if (
                record.gradient_top_opacity < 0
                or record.gradient_top_opacity > 100
                or record.gradient_bottom_opacity < 0
                or record.gradient_bottom_opacity > 100
                or record.credential_opacity < 0
                or record.credential_opacity > 100
            ):
                raise ValidationError("El valor de opacidad debe estar entre 0 y 100.")

    @api.model
    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()
        image_id = param.get_param('pdev_general_utilities.web_background_image_id')
        if image_id:
            image_id = int(image_id)
        gradient_top_opacity = param.get_param('pdev_general_utilities.gradient_top_opacity')
        gradient_bottom_opacity = param.get_param('pdev_general_utilities.gradient_bottom_opacity')
        res.update(
            credential_border=param.get_param('pdev_general_utilities.credential_border', 'without'),
            credential_element_color=param.get_param('pdev_general_utilities.credential_element_color', '#596773'),
            color=param.get_param('pdev_general_utilities.color'),
            background=param.get_param('pdev_general_utilities.background'),
            login_style=param.get_param('pdev_general_utilities.login_style'),
            gradient_top_color=param.get_param('pdev_general_utilities.gradient_top_color'),
            gradient_top_opacity=int(gradient_top_opacity) if gradient_top_opacity else 0,
            gradient_bottom_color=param.get_param('pdev_general_utilities.gradient_bottom_color'),
            gradient_bottom_opacity=int(gradient_bottom_opacity) if gradient_bottom_opacity else 0,
            credential_opacity=int(param.get_param('pdev_general_utilities.credential_opacity', '70')),
            video=param.get_param('pdev_general_utilities.video'),
            b_image_id=image_id,
            web_remove_powered_by=param.get_param('pdev_general_utilities.web_remove_powered_by'),
            disable_passkey=param.get_param('pdev_general_utilities.disable_passkey'),
        )
        return res

    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('pdev_general_utilities.credential_border', self.credential_border or 'without')
        param.set_param('pdev_general_utilities.credential_element_color', self.credential_element_color or '#596773')
        param.set_param('pdev_general_utilities.color', self.color or False)
        param.set_param('pdev_general_utilities.background', self.background or False)
        param.set_param('pdev_general_utilities.login_style', self.login_style or False)
        param.set_param('pdev_general_utilities.gradient_top_color', self.gradient_top_color or False)
        param.set_param('pdev_general_utilities.gradient_top_opacity', self.gradient_top_opacity or 0)
        param.set_param('pdev_general_utilities.gradient_bottom_color', self.gradient_bottom_color or False)
        param.set_param('pdev_general_utilities.gradient_bottom_opacity', self.gradient_bottom_opacity or 0)
        param.set_param('pdev_general_utilities.credential_opacity', self.credential_opacity or 70)
        param.set_param('pdev_general_utilities.video', self.video or False)
        param.set_param('pdev_general_utilities.web_background_image_id', self.b_image_id.id or False)
        param.set_param('pdev_general_utilities.web_remove_powered_by', self.web_remove_powered_by or False)
        param.set_param('pdev_general_utilities.disable_passkey', self.disable_passkey or False)
