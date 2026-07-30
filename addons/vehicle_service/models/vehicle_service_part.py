# -*- coding: utf-8 -*-

from odoo import api, fields, models


class VehicleServicePart(models.Model):
    _name = "vehicle.service.part"
    _description = "Vehicle Service Part"
    _order = "sequence, id"

    name = fields.Text(
        string="Description",
    )
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
        string="Currency",
        related="service_order_id.currency_id",
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Part",
        required=True,
        ondelete="restrict",
        index=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        related="product_id.uom_id",
        string="Unit of Measure",
        readonly=True,
        store=True,
    )

    product_uom_qty = fields.Float(
        string="Quantity",
        default=1.0,
        required=True,
    )
    unit_price = fields.Monetary(
        string="Unit Price",
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
            "vehicle_service_part_quantity_positive",
            "CHECK(product_uom_qty > 0)",
            "Quantity must be greater than zero.",
        ),
        (
            "vehicle_service_part_price_positive",
            "CHECK(unit_price >= 0)",
            "Unit price cannot be negative.",
        ),
    ]

    @api.depends("product_uom_qty", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_uom_qty * line.unit_price

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.name = self.product_id.display_name
        self.unit_price = self.product_id.lst_price
