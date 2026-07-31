# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class VehicleServiceLabour(models.Model):
    _name = "vehicle.service.labour"
    _description = "Vehicle Service Labour"
    _order = "sequence, id"

    name = fields.Char(
        string="Operation",
        required=True,
    )
        # tracking=True,
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    service_order_id = fields.Many2one(
        "vehicle.service.order",
        string="Service Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="service_order_id.company_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="service_order_id.currency_id",
        store=True,
        readonly=True,
    )
    technician_id = fields.Many2one(
        "res.users",
        string="Technician",
        index=True,
    )

    hours = fields.Float(
        string="Hours",
        default=1.0,
        required=True,
    )
    labour_rate = fields.Monetary(
        string="Labour Rate",
        currency_field="currency_id",
        required=True,
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        currency_field="currency_id",
        compute="_compute_subtotal",
        store=True,
    )

    _sql_constraints = [
        (
            "vehicle_service_labour_hours_positive",
            "CHECK(hours > 0)",
            "Hours must be greater than zero.",
        ),
        (
            "vehicle_service_labour_rate_positive",
            "CHECK(labour_rate >= 0)",
            "Labour rate cannot be negative.",
        ),
    ]

    @api.depends("hours", "labour_rate")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (
                line.hours
                * line.labour_rate
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            service_order = self.env[
                "vehicle.service.order"
            ].browse(
                vals["service_order_id"]
            )
            service_order._check_modifiable()
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            line.service_order_id._check_modifiable()
        return super().write(vals)

    def unlink(self):
        for line in self:
            line.service_order_id._check_modifiable()
        return super().unlink()
