# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    workshop_location_id = fields.Many2one(
        "stock.location",
        string="Workshop Stock Location",
        domain=[("usage", "=", "internal")],
        help="Inventory location where workshop technicians consume parts.",
    )
