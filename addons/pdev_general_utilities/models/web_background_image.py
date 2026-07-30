# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class WebBackgroundImage(models.Model):
	_name = 'web.background.image'
	_description = "Background image"
	_rec_name = 'name'

	image = fields.Binary(string="Image")
	name = fields.Char(string="Name")
