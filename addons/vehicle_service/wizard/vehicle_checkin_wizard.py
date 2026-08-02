# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class VehicleCheckinWizard(models.TransientModel):
    _name = "vehicle.checkin.wizard"
    _description = "Vehicle Check-In Wizard"

    vehicle_id = fields.Many2one(
        "vehicle.vehicle",
        string="Vehicle",
        required=True,
        readonly=True,
    )
    owner_id = fields.Many2one(
        "res.partner",
        string="Owner",
        related="vehicle_id.owner_id",
        readonly=True,
    )
    advisor_id = fields.Many2one(
        "res.users",
        string="Service Advisor",
        default=lambda self: self.env.user,
        required=True,
    )

    check_in_odometer = fields.Float(
        string="Current Odometer",
        required=True,
    )
    customer_complaint = fields.Text(
        string="Customer Complaint",
        required=True,
    )
    expected_delivery_date = fields.Date(
        string="Expected Delivery Date",
        default=fields.Date.context_today,
        required=True,
    )
    # Future field. Now, showcase only
    service_type = fields.Selection(
        [
            ("scheduled", "Scheduled Service"),
            ("breakdown", "Breakdown Repair"),
            ("inspection", "Inspection"),
        ],
        string="Service Type",
        default="scheduled",
        required=True,
        help="Classification of the workshop visit.",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_id = self.env.context.get("active_id")
        if not active_id:
            return res
        
        vehicle = self.env["vehicle.vehicle"].browse(active_id)
        res.update({
            "vehicle_id": vehicle.id,
            "check_in_odometer": vehicle.odometer,
        })
        return res

    def action_create_service_order(self):
        self.ensure_one()

        values = {
            "advisor_id": self.advisor_id.id,
            "check_in_odometer": self.check_in_odometer,
            "customer_complaint": self.customer_complaint,
            "expected_delivery_date": self.expected_delivery_date,
            "service_type": self.service_type,
        }

        return self.vehicle_id.action_create_service_order(values)
