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
    manufacturer_id = fields.Many2one(
        "vehicle.manufacturer",
        string="Manufacturer",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    model_id = fields.Many2one(
        "vehicle.model",
        string="Model",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    owner_id = fields.Many2one(
        "res.partner",
        string="Owner",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    owner_mobile = fields.Char(
        string="Owner Mobile",
        related="owner_id.mobile",
        store=True,
        readonly=True,
    )
    owner_email = fields.Char(
        string="Owner Email",
        related="owner_id.email",
        store=True,
        readonly=True,
    )
    registration_date = fields.Date(
        string="Registration Date",
        tracking=True,
    )
    manufacturing_year = fields.Integer(
        string="Manufacturing Year",
    )
    vin_number = fields.Char(
        string="VIN",
        copy=False,
        tracking=True,
        index=True,
    )
    engine_number = fields.Char(
        string="Engine Number",
        copy=False,
    )
    colour = fields.Char(
        string="Colour",
    )
    odometer = fields.Float(
        string="Odometer",
        tracking=True,
    )
    vehicle_age = fields.Integer(
        string="Vehicle Age",
        compute="_compute_vehicle_age",
    )
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

    _sql_constraints = [
        (
            "vehicle_registration_unique",
            "unique(registration_number)",
            "Registration number already exists.",
        ),
        (
            "vehicle_vin_unique",
            "unique(vin_number)",
            "VIN already exists."
        ),
        (
            "vehicle_engine_unique",
            "unique(engine_number)",
            "Engine number already exists."
        ),
    ]

    @api.constrains("manufacturing_year")
    def _check_manufacturing_year(self):
        current_year = date.today().year

        for record in self:
            if (
                record.manufacturing_year
                and record.manufacturing_year > current_year
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

    @api.constrains("manufacturer_id", "model_id")
    def _check_model_belongs_to_manufacturer(self):
        for record in self:
            if (
                record.model_id
                and record.model_id.manufacturer_id != record.manufacturer_id
            ):
                raise ValidationError(
                    "The selected model does not belong to the selected manufacturer."
                )

    @api.depends("parts_cost", "labour_cost")
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = (
                record.parts_cost +
                record.labour_cost
            )

    @api.depends("manufacturing_year")
    def _compute_vehicle_age(self):
        current_year = date.today().year

        for record in self:
            if not record.manufacturing_year:
                record.vehicle_age = 0
                continue
            record.vehicle_age = current_year - record.manufacturing_year

    @api.onchange("manufacturer_id")
    def _onchange_manufacturer_id(self):
        if (
            self.model_id
            and self.model_id.manufacturer_id != self.manufacturer_id
        ):
            self.model_id = False

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
