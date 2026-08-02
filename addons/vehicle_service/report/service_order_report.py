# -*- coding: utf-8 -*-

from odoo import fields, models


class ReportServiceOrderJobCard(models.AbstractModel):
    _name = "report.vehicle_service.service_order_job_card"
    _description = "Vehicle Service Job Card Report"

    def _get_report_values(self, docids, data=None):
        docs = self.env["vehicle.service.order"].browse(docids)

        summary = {
            order.id: self._prepare_summary(order)
            for order in docs
        }

        return {
            "doc_ids": docids,
            "doc_model": "vehicle.service.order",
            "docs": docs,
            "report": {
                "company": self.env.company,
                "generated_by": self.env.user,
                "generated_on": fields.Datetime.now(),
                "version": "v17.0",
                "show_qr": False,
                "summary": summary,
            },
        }

    def _prepare_summary(self, service_order):
        """
        Prepare report specific information.
        Business calculations are intentionally performed here instead
        of inside the QWeb template.
        Returns
        -------
        dict
        """
        labour_count = len(service_order.labour_line_ids)
        part_count = len(service_order.part_line_ids)

        total_labour_hours = sum(
            service_order.labour_line_ids.mapped("hours")
        )
        total_part_quantity = sum(
            service_order.part_line_ids.mapped("product_uom_qty")
        )

        return {
            "labour_count": labour_count,
            "part_count": part_count,
            "total_labour_hours": total_labour_hours,
            "total_part_quantity": total_part_quantity,
            # -----------------------------------------------------------------
            # Empty rows improve printed Job Card appearance.
            # Future:
            # Replace with configurable minimum row count.
            # -----------------------------------------------------------------
            "empty_labour_rows": max(0, 4 - labour_count),
            "empty_part_rows": max(0, 4 - part_count),
        }
