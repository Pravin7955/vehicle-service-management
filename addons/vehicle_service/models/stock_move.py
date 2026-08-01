# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    service_part_line_id = fields.Many2one(
        "vehicle.service.part",
        string="Service Part Line",
        index=True,
        copy=False,
        ondelete="set null",
    )
