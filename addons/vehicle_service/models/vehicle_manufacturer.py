# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VehicleManufacturer(models.Model):
    _name = "vehicle.manufacturer"
    _description = "Vehicle Manufacturer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"
    _rec_name = "name"

    name = fields.Char(
        string="Manufacturer",
        required=True,
        tracking=True,
        index=True,
    )
    code = fields.Char(
        string="Code",
        tracking=True,
        help="Short unique manufacturer code."
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        tracking=True,
    )
    logo = fields.Image(
        string="Logo",
        max_width=512,
        max_height=512,
    )
    website = fields.Char()
    description = fields.Text()
    sequence = fields.Integer(
        default=10,
    )
    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        (
            "manufacturer_name_unique",
            "unique(name)",
            "Manufacturer already exists.",
        ),
        (
            "manufacturer_code_unique",
            "unique(code)",
            "Manufacturer code already exists.",
        ),
    ]

    @api.constrains("name")
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    "Manufacturer name cannot be empty."
                )
