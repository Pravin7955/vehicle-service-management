# -*- coding: utf-8 -*-

from datetime import date
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VehicleVehicle(models.Model):
    _name = "vehicle.vehicle"
    _description = "Vehicle"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    _rec_name = "registration_number"
    _order = "registration_number"

    registration_number = fields.Char(
        string="Registration Number",
        required=True,
        tracking=True,
        copy=False,
        index=True,
        help="Official registration number of the vehicle.",
    )
    make = fields.Char(
        string="Manufacturer",
        index=True,
    )
    model = fields.Char(string="Model")
    year = fields.Integer(string="Manufacturing Year")
    owner_id = fields.Many2one(
        "res.partner",
        string="Owner",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    owner_phone = fields.Char(
        string="Owner Phone",
        related="owner_id.phone",
    )
    owner_email = fields.Char(
        string="Owner Email",
        related="owner_id.email",
    )
    colour = fields.Char(string="Colour")
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    parts_cost = fields.Float(
        string="Parts Cost",
    )
    labour_cost = fields.Float(
        string="Labour Cost",
    )
    total_cost = fields.Float(
        string="Total Cost",
        compute="_compute_total_cost",
        store=True,
    )

    vehicle_age = fields.Integer(
        string="Vehicle Age",
        compute="_compute_vehicle_age",
    )

    _sql_constraints = [
        (
            "unique_registration",
            "unique(registration_number)",
            "Registration number must be unique.",
        ),
    ]

    @api.constrains("year")
    def _check_year(self):
        current_year = date.today().year

        for record in self:
            if (
                record.year
                and record.year > current_year
            ):
                raise ValidationError(
                    "Manufacturing year cannot be in the future."
                )

    @api.constrains("parts_cost", "labour_cost")
    def _check_costs(self):
        for record in self:
            errors = []
            if record.parts_cost < 0:
                errors.append("• Parts cost cannot be negative.")

            if record.labour_cost < 0:
                errors.append("• Labour cost cannot be negative.")

            if errors:
                raise ValidationError("\n".join(errors))

    @api.depends("parts_cost", "labour_cost")
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = (
                record.parts_cost +
                record.labour_cost
            )

    @api.depends("year")
    def _compute_vehicle_age(self):
        current_year = date.today().year

        for record in self:
            if not record.year:
                record.vehicle_age = 0
                continue
            record.vehicle_age = current_year - record.year

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            registration = vals.get("registration_number")
            if registration:
                vals["registration_number"] = self._normalise_registration(registration)

        return super().create(vals_list)

    def write(self, vals):
        registration = vals.get("registration_number")
        if registration:
            vals["registration_number"] = self._normalise_registration(registration)

        return super().write(vals)

    def copy(self, default=None):
        default = dict(default or {})

        default["registration_number"] = (
            f"{self.registration_number}-COPY"
        )

        return super().copy(default)

    def _normalise_registration(self, value):
        return value.upper().strip() if value else value
