# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    vehicle_ids = fields.One2many(
        "vehicle.vehicle",
        "owner_id",
        string="Vehicles",
    )
    service_order_ids = fields.One2many(
        "vehicle.service.order",
        "customer_id",
        string="Service Orders",
    )

    service_order_count = fields.Integer(
        string="Service Order Count",
        compute="_compute_service_order_count",
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

    @api.depends("service_order_ids")
    def _compute_service_order_count(self):
        grouped_data = self.env[
            "vehicle.service.order"
        ].read_group(
            domain=[("customer_id", "in", self.ids)],
            fields=["customer_id"],
            groupby=["customer_id"],
        )

        count_map = {
            item["customer_id"][0]: item["customer_id_count"]
            for item in grouped_data
        }

        for customer in self:
            customer.service_order_count = count_map.get(
                customer.id,
                0,
            )

    def action_view_vehicles(self):
        self.ensure_one()
        action = self.env.ref(
            "vehicle_service.action_vehicle"
        ).read()[0]
        action["view_mode"] = "list,form"
        action["domain"] = [
            ("owner_id","=",self.id)
        ]
        action["context"] = {
            "default_owner_id": self.id,
        }
        return action

    def action_view_service_orders(self):
        self.ensure_one()
        action = self.env.ref(
            "vehicle_service.action_vehicle_service_order"
        ).read()[0]
        action["view_mode"] = "list,form"
        action["domain"] = [
            ("customer_id","=",self.id)
        ]
        action["context"] = {
            "default_customer_id": self.id,
        }
        return action
