# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    vehicle_ids = fields.One2many(
        "vehicle.vehicle",
        "owner_id",
        string="Vehicles",
    )
    vehicle_count = fields.Integer(
        string="Vehicle Count",
        compute="_compute_vehicle_count",
    )

    @api.depends("vehicle_ids")
    def _compute_vehicle_count(self):
        counts = self.env["vehicle.vehicle"].read_group(
            domain=[("owner_id", "in", self.ids)],
            fields=["owner_id"],
            groupby=["owner_id"],
        )

        mapped_counts = {
            record["owner_id"][0]: record["owner_id_count"]
            for record in counts
        }

        for partner in self:
            partner.vehicle_count = mapped_counts.get(
                partner.id,
                0,
            )

    def action_view_vehicles(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Vehicles",
            "res_model": "vehicle.vehicle",
            "view_mode": "list,form",
            "domain": [
                ("owner_id", "=", self.id)
            ],
            "context": {
                "default_owner_id": self.id,
            },
        }
