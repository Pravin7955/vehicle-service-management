# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    workshop_location_id = fields.Many2one(
        string="Workshop Location",
        related="company_id.workshop_location_id",
        readonly=False,
    )
