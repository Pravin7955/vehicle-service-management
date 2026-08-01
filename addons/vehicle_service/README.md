# Vehicle Service Management

A production-oriented **Vehicle Service Management** module for **Odoo 17**, built as a learning project to master Odoo development while following enterprise-grade software engineering practices.

> **Current Version:** v0.5.2 Stable

---

# Project Goal

The purpose of this project is not only to build a Vehicle Service Management System, but also to learn Odoo deeply by implementing real-world ERP concepts.

The project follows three major principles:

- Learn Odoo through practical implementation.
- Follow Odoo coding standards and best practices.
- Build a scalable and production-ready architecture.

Every feature is designed as if it were being developed for a real business deployment.

---

# Current Features

## Vehicle Management

- Vehicle Master
- Manufacturer Master
- Vehicle Model Master
- Owner Integration (res.partner)
- Vehicle History
- Smart Buttons

---

## Service Orders

- Service Order Workflow
- Service Advisor
- Customer Complaint
- Odometer Tracking
- Internal Notes
- Chatter Integration
- Activity Support

Workflow:

```
Draft
    ↓
Confirmed
    ↓
In Progress
    ↓
Completed

        OR

Cancelled
```

---

## Labour Management

- Labour Line Items
- Technician Assignment
- Labour Hours
- Labour Rate
- Automatic Cost Calculation

---

## Parts Management

- Part Line Items
- Product Integration
- Automatic Pricing
- Quantity Tracking
- Cost Calculation
- Stock Move Mapping

---

## Inventory Integration

- Stock Picking Creation
- Internal Transfers
- Stock Move Synchronization
- Inventory Reservation
- Reservation Status
- Synchronization Status
- Idempotent Synchronization Engine

---

## Smart Navigation

- Vehicle → Service Orders
- Customer → Vehicles
- Customer → Service Orders
- Service Order → Stock Picking

---

## Financial Summary

Automatically computes:

- Labour Cost
- Parts Cost
- Total Cost

---

# Technical Highlights

## ORM

This project demonstrates:

- Computed Fields
- Related Fields
- SQL Constraints
- Python Constraints
- Onchange Methods
- Model Inheritance
- Mail Thread
- Mail Activities
- Stored Computed Fields
- Readonly Workflow Fields
- Smart Buttons
- Search Views
- Window Actions

---

## Inventory

Current implementation includes:

- stock.picking
- stock.move
- Internal Transfers
- Reservation Workflow
- Synchronization Engine

---

## Workflow

Implemented workflow guard methods:

- `_check_can_confirm()`
- `_check_can_start()`
- `_check_can_sync_inventory()`
- `_check_can_reserve_inventory()`
- `_check_can_complete()`
- `_check_can_cancel()`

These ensure business rules remain centralized and maintainable.

---

# Module Structure

```
vehicle_service/

├── controllers/
├── data/
├── models/
│   ├── vehicle.py
│   ├── vehicle_make.py
│   ├── vehicle_model.py
│   ├── vehicle_service_order.py
│   ├── vehicle_service_labour.py
│   ├── vehicle_service_part.py
│   ├── res_company.py
│   ├── res_config_settings.py
│   └── ...
├── security/
├── views/
├── wizard/
├── report/
├── static/
└── README.md
```

---

# Development Principles

The project follows these design principles.

## Separation of Responsibilities

- Master Data
- Transaction Models
- Inventory Logic
- Workflow Logic
- UI Logic

Each responsibility is implemented independently.

---

## Production-Oriented Architecture

The module is designed to be:

- Modular
- Scalable
- Maintainable
- Easy to extend
- Suitable for real deployments

---

## Odoo Best Practices

The project intentionally follows:

- ORM-first development
- Minimal SQL
- Reusable helper methods
- Workflow guard methods
- Small business methods
- Proper tracking
- Company-aware configuration
- Multi-company compatibility

---

# Version History

## v0.5.2 Stable

### Added

- Vehicle Service Order
- Labour Lines
- Parts Lines
- Inventory Synchronization
- Reservation Workflow
- Stock Picking Integration
- Smart Buttons
- Service History
- Company Inventory Configuration

### Improved

- Inventory Synchronization Engine
- Workflow Validation
- Reservation Status
- Code Organization
- Inventory Helpers
- XML Views
- Search Views

### Fixed

- Duplicate Stock Moves
- Inventory Synchronization
- Reservation Bugs
- Workflow Validation
- Product Replacement
- Quantity Synchronization

---

# Known Limitations

The following items are intentionally postponed to future versions.

## Inventory

Workshop inventory currently performs an internal transfer only.

Actual inventory consumption will be introduced in a future version.

---

## Search Filters

The following filters are temporarily disabled:

- Today
- This Month

They will be reintroduced with proper timezone-aware implementation.

---

## Picking Type

Currently determined automatically.

Future versions will allow company-specific configuration.

---

# Future Roadmap

## Version 0.6

Workshop Operations

- Technician Assignment
- Inspection Checklist
- Job Cards
- Attachments
- Images
- Mail Activities
- Calendar View
- Kanban View

---

## Version 0.7

Advanced Inventory

- Workshop Inventory
- Parts Consumption
- Technician Stock
- Returns
- Lots
- Serial Numbers
- Multi-Warehouse

---

## Version 0.8

Customer Experience

- Customer Portal
- Online Service Tracking
- Appointment Booking
- Email Notifications
- SMS Notifications

---

## Version 0.9

Accounting

- Estimates
- Quotations
- Customer Invoices
- Payments
- Warranty
- Credit Notes

---

## Version 1.0

Enterprise Release

- Dashboards
- OWL Components
- Reports
- Testing
- Docker Deployment
- CI/CD
- Documentation
- Performance Optimization

---

# Learning Objectives

This repository is intended to cover the complete Odoo development ecosystem.

Topics include:

- ORM
- Views
- Security
- Inventory
- Accounting
- Reporting
- Website
- Portal
- JavaScript (OWL)
- REST APIs
- Performance
- Testing
- Deployment

The goal is to become proficient in enterprise Odoo development through a real-world project.

---

# Requirements

- Odoo 17
- PostgreSQL
- Python 3.10+
- wkhtmltopdf (for future reporting features)

---

# Installation

1. Copy the module into the Odoo addons directory.

2. Update the Apps List.

3. Install the **Vehicle Service** module.

4. Configure:

- Workshop Stock Location
- Internal Picking Type
- Service Order Sequence

5. Start creating Vehicles and Service Orders.

---

# Development Workflow

Git strategy:

```
main
    │
    ├── feature/vehicle-master
    ├── feature/service-order
    ├── feature/workshop-operations
    └── feature/portal
```

Every feature is developed in its own branch and merged through Pull Requests after code review and regression testing.

---

# License

This project is currently maintained as a personal learning and portfolio project.

Future licensing will be decided before the first public release.

---

# Author

**Pravin Panchal**

Built with the objective of mastering Odoo development through a production-oriented Vehicle Service Management System.

---