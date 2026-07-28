# -*- coding: utf-8 -*-

from odoo import fields, models


class VehicleVehicle(models.Model):
    _name = "vehicle.vehicle"
    _description = "Vehicle"
    _rec_name = "registration_number"
    _order = "registration_number"

    registration_number = fields.Char(
        string="Registration Number",
        required=True,
        copy=False,
    )
    make = fields.Char(string="Manufacturer")
    model = fields.Char(string="Model")
    year = fields.Integer(string="Manufacturing Year")
    active = fields.Boolean(default=True)
