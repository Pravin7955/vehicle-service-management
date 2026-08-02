# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

from odoo.tools.float_utils import float_compare

from urllib.parse import urljoin


class VehicleServiceOrder(models.Model):
    _name = "vehicle.service.order"
    _description = "Vehicle Service Order"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "portal.mixin",
    ]
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
    completion_datetime = fields.Datetime(
        string="Completion Time"
    )
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
    reservation_state = fields.Selection(
        [
            ("not_reserved", "Not Reserved"),
            ("partial", "Partially Reserved"),
            ("reserved", "Reserved"),
            ("consumed", "Consumed"),
        ],
        string="Reservation Status",
        compute="_compute_reservation_state",
        store=True,
        readonly=True,
    )
    inventory_sync_state = fields.Selection(
        [
            ("pending", "Pending Synchronization"),
            ("synchronized", "Synchronized"),
            ("outdated", "Needs Synchronization"),
        ],
        string="Inventory Synchronization",
        default="pending",
        tracking=True,
        copy=False,
    )
    stock_picking_count = fields.Integer(
        compute="_compute_stock_picking_count",
    )

    # Revisite in future and remove if not usecase.
    public_status_url = fields.Char(
        string="Public Status URL",
        compute="_compute_public_status_url",
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

    @api.depends(
        "stock_picking_id.state",
        "stock_picking_id.move_ids.state",
        "stock_picking_id.move_ids.product_uom_qty",
        "stock_picking_id.move_ids.quantity",
    )
    def _compute_reservation_state(self):
        """
        Compute reservation status of the service order.
        States: not_reserved, partial, reserved, consumed
        """
        for order in self:
            picking = order.stock_picking_id
            if not picking:
                order.reservation_state = "not_reserved"
                continue

            moves = picking.move_ids.filtered(
                lambda move: move.state != "cancel"
            )
            if not moves:
                order.reservation_state = "not_reserved"
                continue

            if all(move.state == "done" for move in moves):
                order.reservation_state = "consumed"
                continue

            total_required = 0.0
            total_reserved = 0.0
            for move in moves:
                total_required += move.product_uom_qty
                total_reserved += move.quantity

            if float_compare(
                total_reserved,
                0.0,
                precision_rounding=1e-6,
            ) == 0:
                order.reservation_state = "not_reserved"
            elif float_compare(
                total_reserved,
                total_required,
                precision_rounding=1e-6,
            ) >= 0:
                order.reservation_state = "reserved"
            else:
                order.reservation_state = "partial"

    def _compute_stock_picking_count(self):
        """If in future one order supports multiple pickings 
        nothing changes in XML. Only compute changes. 
        That's designing for future growth."""
        for order in self:
            order.stock_picking_count = 1 if order.stock_picking_id else 0

    def _compute_public_status_url(self):
        """
        Compute service status URL for public.
        It uses Access token to generate URL.
        Added for developement purpuses.

        Revisite in future and remove if not usecase.
        """
        base_url = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url"
        )

        for order in self:
            order._portal_ensure_token()

            order.public_status_url = urljoin(
                base_url,
                f"/service/status/{order.access_token}",
            )

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
    
    @api.model
    def get_by_access_token(self, access_token):
        """
        @api.model used.
        Method can work without record instance.
        Helper method to get record by access_token.
        """
        return self.sudo().search(
            [("access_token", "=", access_token)],
            limit=1,
        )

    # -------------------------------------------------------------------------
    # Workflow Guard Methods
    # -------------------------------------------------------------------------
    
    def _check_modifiable(self):
        self.ensure_one()

        if self._is_locked():
            raise UserError(
                "Completed or cancelled Service Orders cannot be modified."
            )

    def _check_can_confirm(self):
        invalid_orders = self.filtered(
            lambda order: order.state != "draft"
        )
        if invalid_orders:
            raise UserError(
                _("Only draft service orders can be confirmed.")
            )

    def _check_can_start(self):
        self.ensure_one()
        
        if self.state != "confirmed":
            raise UserError(
                _("Only confirmed service orders can be started.")
            )

    def _check_can_sync_inventory(self):
        self.ensure_one()

        if self.state in ("completed", "cancelled"):
            raise UserError(
                _("Inventory cannot be synchronized for completed or cancelled service orders.")
            )

    def _check_can_reserve_inventory(self):
        self.ensure_one()

        if self.state not in ("confirmed", "in_progress"):
            raise UserError(
                _("Inventory can only be reserved for confirmed or in-progress service orders.")
            )

        if not self.stock_picking_id:
            raise UserError(
                _("Please synchronize the document first.")
            )

    def _check_can_complete(self):
        self.ensure_one()

        if self.state != "in_progress":
            raise UserError(
                _("Only repairs in progress can be completed.")
            )

        if self.inventory_sync_state != "synchronized":
            raise UserError(
                _("Please synchronize inventory before completing the repair.")
            )

        if not self.stock_picking_id:
            raise UserError(
                _("No inventory document found.")
            )

    def _check_can_cancel(self):
        self.ensure_one()

        if self.state == "completed":
            raise UserError(
                _("Completed service orders cannot be cancelled.")
            )
        
    # -------------------------------------------------------------------------
    # Workflow Actions
    # -------------------------------------------------------------------------

    def action_confirm(self):
        self._check_can_confirm()

        self.write({
            "state": "confirmed",
        })
        return True

    def action_start(self):
        self.ensure_one()
        self._check_can_start()

        self.write({
            "state": "in_progress",
        })
        return True

    def action_complete(self):
        self.ensure_one()
        self._check_can_complete()

        result = self._validate_inventory()
        if isinstance(result, dict):
            return result

        self.write({
            "state": "completed",
            "completion_datetime": fields.Datetime.now(),
        })

        return True

    def action_cancel(self):
        self.ensure_one()
        self._check_can_cancel()

        self._cancel_inventory()
        self.write({"state": "cancelled"})

        return True

    def action_sync_inventory(self):
        """
        Synchronize the service order document with Inventory.
        Responsibilities:
            - Ensure stock picking exists.
            - Synchronize stock moves.
            - Remove obsolete stock moves.
            - Mark document synchronized.
        This method DOES NOT perform reservation.
        """
        self.ensure_one()
        self._check_can_sync_inventory()

        self._ensure_stock_picking()
        self._sync_stock_moves()
        self._remove_obsolete_stock_moves()

        self.write({
            "inventory_sync_state": "synchronized",
        })

        return True

    def action_reserve_inventory(self):
        """
        Reserve the Inventory.
        """
        self.ensure_one()
        self._check_can_reserve_inventory()

        return self._reserve_inventory()
    
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

    # -------------------------------------------------------------------------
    # Inventory Helpers
    # -------------------------------------------------------------------------

    def _is_locked(self):
        self.ensure_one()

        return self.state in (
            "completed",
            "cancelled",
        )

    def _mark_inventory_outdated(self):
        self.write({
            "inventory_sync_state": "outdated",
        })

    def _get_workshop_location(self):
        self.ensure_one()

        location = self.company_id.workshop_location_id
        if not location:
            raise UserError(
                "Please configure Workshop Stock Location from Settings."
            )
        
        return location

    def _get_internal_picking_type(self):
        """Return Internal Picking Type for current company."""
        self.ensure_one()

        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "internal"),
                ("warehouse_id.company_id", "=", self.company_id.id),
            ],
            limit=1,
        )
        if not picking_type:
            raise UserError(
                "No Internal Picking Type configured for this company."
            )
        return picking_type

    def _ensure_stock_picking(self):
        """
        Ensure a stock picking exists.
        """
        self.ensure_one()

        if self.stock_picking_id:
            return self.stock_picking_id

        return self._create_stock_picking()

    def _create_stock_picking(self):
        self.ensure_one()

        picking = self.env["stock.picking"].create(
            self._prepare_picking_vals()
        )
        self.write({
            "stock_picking_id": picking.id,
        })

        return picking

    def _prepare_picking_vals(self):
        self.ensure_one()

        picking_type = self._get_internal_picking_type()

        return {
            "origin": self.name,
            "partner_id": self.customer_id.id,
            "company_id": self.company_id.id,
            "picking_type_id": picking_type.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": self._get_workshop_location().id,
        }

    def _reserve_inventory(self):
        self.ensure_one()

        picking = self.stock_picking_id
        if picking.state == "draft":
            picking.action_confirm()

        picking.action_assign()

        return True

    def _validate_inventory(self):
        """Validate the stock picking and consume reserved inventory."""
        self.ensure_one()

        picking = self.stock_picking_id
        if not picking:
            raise UserError(
                _("Please synchronize inventory.")
            )

        result = picking.button_validate()
        if isinstance(result, dict):
            return result

        return True

    def _cancel_inventory(self):
        self.ensure_one()

        picking = self.stock_picking_id
        if not picking:
            return

        assigned_moves = picking.move_ids.filtered(
            lambda move: move.state == "assigned"
        )
        if assigned_moves:
            assigned_moves._do_unreserve()

        draft_moves = picking.move_ids.filtered(
            lambda move: move.state not in ("done", "cancel")
        )
        if draft_moves:
            draft_moves._action_cancel()

        if picking.state != "cancel":
            picking.action_cancel()

        return True

    def _sync_stock_moves(self):
        """
        Synchronize service part lines with stock moves.

        This method is idempotent.
        Running it multiple times produces the same result.
        """
        self.ensure_one()

        for part_line in self.part_line_ids.filtered(lambda l: l.product_id):
            active_move = part_line.stock_move_ids.filtered(
                lambda m: m.state != "cancel"
            )[:1]

            if not active_move:
                self._create_stock_move(part_line)
                continue

            if active_move.product_id != part_line.product_id:
                self._replace_stock_move(part_line, active_move)
                continue

            self._update_stock_move(part_line, active_move)

    def _replace_stock_move(self, part_line, move):
        """
        Product changed.
        Replace the move instead of updating it.
        """
        self.ensure_one()

        self._delete_stock_move(move)
        self._create_stock_move(part_line)

    def _create_stock_move(self, part_line):
        """
        Create a stock move for a service part.
        """
        move = self.env["stock.move"].create(
            self._prepare_stock_move_vals(part_line)
        )
        move.write({
            "service_part_line_id": part_line.id,
        })

        return move

    def _update_stock_move(self, part_line, move):
        """
        Update mutable attributes of a stock move.
        Product is intentionally immutable.
        """
        vals = {}

        if move.name != part_line.name:
            vals["name"] = part_line.name

        if move.product_uom_qty != part_line.product_uom_qty:
            vals["product_uom_qty"] = part_line.product_uom_qty

        if not vals:
            return

        self._refresh_move(move, vals)

    def _refresh_move(self, move, vals):
        """
        Refresh an existing move safely.
        Reserved moves must first be unreserved.
        """
        if move.state == "assigned":
            move._do_unreserve()

        move.write(vals)

        if move.state in ("draft", "confirmed", "waiting"):
            move._action_confirm()

    def _remove_obsolete_stock_moves(self):
        """
        Remove stock moves no longer linked
        to any service part.
        """
        self.ensure_one()

        valid_lines = self.part_line_ids

        for move in self.stock_picking_id.move_ids.filtered(
            lambda m: m.state != "cancel"
        ):
            if move.service_part_line_id in valid_lines:
                continue
            self._delete_stock_move(move)

    def _delete_stock_move(self, move):
        """
        Delete a stock move safely.
        """
        if move.state == "done":
            raise UserError(
                _("Completed inventory movements cannot be deleted.")
            )

        if move.state == "assigned":
            move._do_unreserve()

        if move.state != "cancel":
            move._action_cancel()

        move.unlink()

    def _prepare_stock_move_vals(self, part_line):
        self.ensure_one()

        picking = self.stock_picking_id
        picking_type = picking.picking_type_id

        return {
            "name": part_line.name or part_line.product_id.display_name,
            "company_id": self.company_id.id,
            "product_id": part_line.product_id.id,
            "product_uom_qty": part_line.product_uom_qty,
            "product_uom": part_line.product_uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": self._get_workshop_location().id,
            "picking_id": picking.id,
            "origin": self.name,
        }

    # -------------------------------------------------------------------------
    # Public Website
    # -------------------------------------------------------------------------

    def _prepare_public_status_context(self):
        """
        Prepare context used by the public website page.

        Controllers should remain thin and delegate all
        presentation preparation to the business model.
        """

        self.ensure_one()

        return {
            "workflow_steps": self._prepare_workflow_steps(),
            "last_updated": self.write_date,
            "status_color": self._get_status_color(),
            "status_label": dict(
                self._fields["state"].selection
            ).get(self.state),
        }

    def _prepare_workflow_steps(self):
        """
        Prepare workshop workflow progress.
        """
        self.ensure_one()

        workflow = [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ]

        # Completed
        if self.state == "completed":
            return [
                {
                    "state": state,
                    "label": label,
                    "status": "done",
                    "icon": "✓",
                    "color": "success",
                }
                for state, label in workflow
            ]

        # Cancelled
        if self.state == "cancelled":
            result = []
            reached_cancel = False

            for state, label in workflow:
                if state == "completed":
                    break
                if not reached_cancel:
                    result.append({
                        "state": state,
                        "label": label,
                        "status": "done",
                        "icon": "✓",
                        "color": "success",
                    })

            result.append({
                "state": "cancelled",
                "label": "Cancelled",
                "status": "cancelled",
                "icon": "✕",
                "color": "danger",
            })
            return result

        current_index = next(
            (
                index
                for index, (state, _) in enumerate(workflow)
                if state == self.state
            ),
            -1,
        )

        result = []

        for index, (state, label) in enumerate(workflow):
            if index < current_index:
                result.append({
                    "state": state,
                    "label": label,
                    "status": "done",
                    "icon": "✓",
                    "color": "success",
                })
            elif index == current_index:
                result.append({
                    "state": state,
                    "label": label,
                    "status": "current",
                    "icon": "●",
                    "color": "warning",
                })
            else:
                result.append({
                    "state": state,
                    "label": label,
                    "status": "pending",
                    "icon": "○",
                    "color": "secondary",
                })

        return result

    def _get_status_color(self):
        self.ensure_one()

        return {
            "draft": "secondary",
            "confirmed": "primary",
            "in_progress": "warning",
            "completed": "success",
            "cancelled": "danger",
        }.get(self.state, "secondary")
