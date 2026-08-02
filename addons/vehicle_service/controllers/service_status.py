# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class VehicleServiceController(http.Controller):

    @http.route(
        "/service/status/<string:access_token>",
        type="http",
        auth="public",
        website=True,
    )
    def service_status(self, access_token, **kwargs):

        service_order = request.env[
            "vehicle.service.order"
        ].get_by_access_token(access_token)

        if not service_order:
            return request.not_found()

        values = {
            "service_order": service_order,
        }
        values.update(
            service_order._prepare_public_status_context()
        )

        return request.render(
            "vehicle_service.website_service_status",
            values,
        )
