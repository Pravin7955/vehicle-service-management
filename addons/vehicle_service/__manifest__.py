{
    "name": "Vehicle Service Management",

    "summary": "Manage vehicle servicing, repairs, job cards and service history.",

    "description": """
                    Vehicle Service Management

                    A complete Odoo module for managing
                    customers, vehicles, service orders,
                    job cards and repair history.

                    Developed as a production-style learning project.
                    """,

    "author": "Pravin Panchal",

    "website": "https://github.com/Pravin7955/vehicle-service-management",

    "category": "Services",

    "version": "17.0.1.0.1",

    "license": "LGPL-3",

    "depends": [
        "mail",
        "contacts",
        "product",
        "stock",
    ],

    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/vehicle_rules.xml",
        "data/ir_sequence.xml",
        "data/stock_location_data.xml",
        "views/vehicle_views.xml",
        "views/vehicle_manufacturer_views.xml",
        "views/vehicle_model_views.xml",
        "views/res_partner_views.xml",
        "views/vehicle_service_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu.xml",
    ],

    "demo": [
        "demo/manufacturer_demo.xml",
        "demo/model_demo.xml",
    ],

    "assets": {

    },

    "application": True,

    "installable": True,

    "auto_install": False,
}