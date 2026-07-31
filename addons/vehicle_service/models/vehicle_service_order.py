# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class VehicleServiceOrder(models.Model):
    _name = "vehicle.service.order"
    _description = "Vehicle Service Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "check_in_datetime desc, id desc"

    name = fields.Char(
        string="Service Order",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
        index=True,
    )
    vehicle_id = fields.Many2one(
        "vehicle.vehicle",
        string="Vehicle",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )
    advisor_id = fields.Many2one(
        "res.users",
        string="Service Advisor",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        index=True,
    )
    stock_picking_id = fields.Many2one(
        "stock.picking",
        string="Stock Picking",
        readonly=True,
        copy=False,
        index=True,
    )
    labour_line_ids = fields.One2many(
        "vehicle.service.labour",
        "service_order_id",
        string="Labour Lines",
        copy=True,
    )
    part_line_ids = fields.One2many(
        "vehicle.service.part",
        "service_order_id",
        string="Parts",
        copy=True,
    )
    
    check_in_datetime = fields.Datetime(
        string="Check-In",
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    # Maybe usefull in future so need to check it later
    # service_date = fields.Date(
    #     string="Service Date",
    #     related="check_in_datetime",
    #     store=True,
    #     readonly=True,
    # )
    expected_delivery_date = fields.Date(
        string="Expected Delivery",
        tracking=True,
    )
    labour_cost = fields.Monetary(
        string="Labour Cost",
        currency_field="currency_id",
        compute="_compute_labour_cost",
        store=True,
        tracking=True,
    )
    parts_cost = fields.Monetary(
        string="Parts Cost",
        currency_field="currency_id",
        compute="_compute_parts_cost",
        store=True,
    )
    total_cost = fields.Monetary(
        string="Total Cost",
        currency_field="currency_id",
        compute="_compute_total_cost",
        store=True,
    )

    customer_complaint = fields.Text(
        string="Customer Complaint",
        required=True,
        tracking=True,
    )
    odometer = fields.Float(
        string="Odometer",
        digits=(16, 1),
        tracking=True,
    )
    notes = fields.Html(
        string="Internal Notes",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        index=True,
    )
    inventory_status = fields.Selection(
        [
            ("not_reserved", "Not Reserved"),
            ("waiting", "Waiting"),
            ("reserved", "Reserved"),
            ("done", "Consumed"),
        ],
        string="Inventory Status",
        compute="_compute_inventory_status",
    )
    stock_picking_count = fields.Integer(
        compute="_compute_stock_picking_count",
    )

    _sql_constraints = [
        (
            "vehicle_service_order_name_unique",
            "unique(name)",
            "The service order number must be unique.",
        ),
    ]

    @api.constrains("expected_delivery_date", "check_in_datetime")
    def _check_expected_delivery_date(self):
        for record in self:
            if (
                record.expected_delivery_date
                and record.expected_delivery_date < record.check_in_datetime.date()
            ):
                raise ValidationError(
                    "Expected delivery date cannot be earlier than the service date."
                )

    @api.depends("labour_line_ids.subtotal")
    def _compute_labour_cost(self):
        for order in self:
            order.labour_cost = sum(
                order.labour_line_ids.mapped(
                    "subtotal"
                )
            )

    @api.depends("part_line_ids.subtotal")
    def _compute_parts_cost(self):
        for order in self:
            order.parts_cost = sum(
                order.part_line_ids.mapped(
                    "subtotal"
                )
            )

    @api.depends("labour_cost", "parts_cost")
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = (
                order.labour_cost
                + order.parts_cost
            )

    @api.depends("stock_picking_id.state")
    def _compute_inventory_status(self):
        mapping = {
            "draft": "not_reserved",
            "confirmed": "waiting",
            "waiting": "waiting",
            "assigned": "reserved",
            "done": "done",
            "cancel": "not_reserved",
        }
        for order in self:
            if order.stock_picking_id:
                order.inventory_status = mapping.get(
                    order.stock_picking_id.state,
                    "not_reserved",
                )
            else:
                order.inventory_status = "not_reserved"

    def _compute_stock_picking_count(self):
        """If in future one order supports multiple pickings 
        nothing changes in XML. Only compute changes. 
        That's designing for future growth."""
        for order in self:
            order.stock_picking_count = 1 if order.stock_picking_id else 0

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.customer_id = self.vehicle_id.owner_id
            self.odometer = self.vehicle_id.odometer

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to add sequence"""
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"]
                    .next_by_code("vehicle.service.order")
                    or "New"
                )
        return super().create(vals_list)

    def write(self, vals):
        locked_fields = {
            "vehicle_id",
            "customer_id",
            "check_in_datetime",
            "expected_delivery_date",
        }
        if locked_fields.intersection(vals):
            for order in self:
                if order.state == "draft":
                    continue
                raise UserError(
                    "General information cannot be modified after confirmation."
                )
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    "Only draft service orders can be deleted."
                )
        return super().unlink()

    def action_confirm(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    "Only draft orders can be confirmed."
                )
            record.state = "confirmed"

    def action_start(self):
        for record in self:
            if record.state != "confirmed":
                raise UserError(
                    "Only confirmed service orders can be started."
                )
            record.state = "in_progress"

    def action_complete(self):
        for record in self:
            if record.state != "in_progress":
                raise UserError(
                    "Only service orders in progress can be completed."
                )
            record.state = "completed"

    def action_cancel(self):
        for record in self:
            record.state = "cancelled"

    def action_reserve_parts(self):
        self.ensure_one()

        raise NotImplementedError(
            "Implemented in Lesson 5.2C"
        )

    def action_view_stock_picking(self):
        self.ensure_one()
        if not self.stock_picking_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": "Stock Picking",
            "res_model": "stock.picking",
            "view_mode": "form",
            "res_id": self.stock_picking_id.id,
            "target": "current",
        }

    def _is_editable(self):
        self.ensure_one()
        return self.state in (
            "draft",
            "confirmed",
            "in_progress",
        )

    def _is_locked(self):
        self.ensure_one()
        return self.state in (
            "completed",
            "cancelled",
        )

    def _check_modifiable(self):
        self.ensure_one()
        if self._is_locked():
            raise UserError(
                "Completed or cancelled Service Orders cannot be modified."
            )

    def _get_workshop_location(self):
        self.ensure_one()
        location = self.company_id.workshop_location_id
        if not location:
            raise UserError(
                "Please configure Workshop Stock Location from Settings."
            )
        return location
