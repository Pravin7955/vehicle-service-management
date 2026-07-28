# -*- coding: utf-8 -*-

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    vehicle_ids = fields.One2many(
        "vehicle.vehicle",
        "owner_id",
        string="Vehicles",
    )
