# -*- coding: utf-8 -*-

from odoo import fields, models


class VehicleVehicle(models.Model):
    _name = "vehicle.vehicle"
    _description = "Vehicle"

    name = fields.Char(
        string="Vehicle Name",
        required=True,
    )
