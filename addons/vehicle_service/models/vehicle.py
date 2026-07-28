# -*- coding: utf-8 -*-

from odoo import api, fields, models


class VehicleVehicle(models.Model):
    _name = "vehicle.vehicle"
    _description = "Vehicle"
    _rec_name = "registration_number"
    _order = "registration_number"

    registration_number = fields.Char(
        string="Registration Number",
        required=True,
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
        index=True,
        ondelete="restrict",
    )
    colour = fields.Char(string="Colour")
    active = fields.Boolean(
        string="Active",
        default=True,
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

    @api.depends("parts_cost", "labour_cost")
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = (
                record.parts_cost +
                record.labour_cost
            )
