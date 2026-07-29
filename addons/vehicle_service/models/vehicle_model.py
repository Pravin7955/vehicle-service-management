# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VehicleModel(models.Model):
    _name = "vehicle.model"
    _description = "Vehicle Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "manufacturer_id, sequence, name"
    _rec_name = "name"

    name = fields.Char(
        string="Model",
        required=True,
        tracking=True,
        index=True,
    )
    manufacturer_id = fields.Many2one(
        "vehicle.manufacturer",
        string="Manufacturer",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    code = fields.Char(
        string="Code",
        tracking=True,
        help="Unique short code for the vehicle model.",
    )
    description = fields.Text(
        string="Description",
    )
    sequence = fields.Integer(
        default=10,
    )
    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        (
            "manufacturer_model_unique",
            "unique(name, manufacturer_id)",
            "This manufacturer already has a model with this name.",
        ),
        (
            "vehicle_model_code_unique",
            "unique(code)",
            "Vehicle model code must be unique.",
        ),
    ]

    @api.constrains("name")
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    "Vehicle model name cannot be empty."
                )
