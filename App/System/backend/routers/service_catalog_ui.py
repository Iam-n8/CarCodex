# --------------------------------------------------
# service_catalog_ui.py
#
# Service Catalog UI / Setup Routes
#
# Purpose:
# - Own service groups and service items
# - Keep service catalog separate from vehicle_ui.py
# - Provide exact service items for maintenance-add,
#   MaintSch, and Maintenance Due matching
# --------------------------------------------------


from fastapi import (
    APIRouter,
    Request
)

from database import (
    SessionLocal
)

from models import (
    ServiceGroup,
    ServiceItem
)

from fastapi.responses import (
    HTMLResponse
)

from shared.template_loader import (
    templates
)

from helpers.service_catalog_loader import (
    load_vehicle_service_catalog_rows,
    load_service_catalog_rows_for_domain,
    load_available_domains,
    clean_csv_value,
    csv_int,
    csv_bool
)
router = APIRouter()

# --------------------------------------------------
# Service Catalog CSV
# --------------------------------------------------

# --------------------------------------------------
# Seed Default Service Catalog
# --------------------------------------------------

@router.post(
    "/service-catalog/seed-defaults"
)
def seed_default_service_catalog():

    db = SessionLocal()

    existing_groups = db.query(
        ServiceGroup
    ).all()

    if existing_groups:

        db.close()

        return {
            "message": "Service catalog already exists",
            "groups_created": 0,
            "items_created": 0
        }

    catalog_rows = load_vehicle_service_catalog_rows()

    groups_by_code = {}

    groups_created = 0

    items_created = 0

    for row in catalog_rows:

        domain = clean_csv_value(
            row.get(
                "domain"
            )
        )

        group_code = csv_int(
            row.get(
                "group_code"
            ),
            default=0
        )

        group_name = clean_csv_value(
            row.get(
                "group_name"
            )
        )

        service_code = csv_int(
            row.get(
                "service_code"
            ),
            default=0
        )

        service_item = clean_csv_value(
            row.get(
                "service_item"
            )
        )

        service_type_match = clean_csv_value(
            row.get(
                "service_type_match"
            )
        )

        service_category = clean_csv_value(
            row.get(
                "service_category"
            )
        )

        track_for_maintenance_due = csv_bool(
            row.get(
                "track_for_maintenance_due"
            )
        )

        default_miles_interval = csv_int(
            row.get(
                "default_miles_interval"
            ),
            default=0
        )

        default_period_months = csv_int(
            row.get(
                "default_period_months"
            ),
            default=0
        )

        notes = clean_csv_value(
            row.get(
                "notes"
            )
        )

        if (
            not domain
            or not group_name
            or not service_item
            or group_code == 0
            or service_code == 0
        ):

            continue

        group_key = (
            domain.lower(),
            group_code
        )

        if group_key not in groups_by_code:

            group = ServiceGroup(

                domain=domain,

                group_code=group_code,

                name=group_name,

                display_order=group_code,

                inactive=False,

                notes=""

            )

            db.add(
                group
            )

            db.flush()

            groups_by_code[group_key] = group

            groups_created += 1

        group = groups_by_code[
            group_key
        ]

        if not service_type_match:

            service_type_match = service_item

        item = ServiceItem(

            group_id=group.id,

            domain=domain,

            service_code=service_code,

            item_name=service_item,

            service_type_match=service_type_match,

            service_category=service_category,

            track_for_maintenance_due=(
                track_for_maintenance_due
            ),

            default_miles_interval=(
                default_miles_interval
                if default_miles_interval > 0
                else None
            ),

            default_period_months=(
                default_period_months
                if default_period_months > 0
                else None
            ),

            display_order=service_code,

            inactive=False,

            notes=notes

        )

        db.add(
            item
        )

        items_created += 1

    db.commit()

    db.close()

    return {
        "message": "Default service catalog created from CSV",
        "groups_created": groups_created,
        "items_created": items_created
    }

# --------------------------------------------------
# Service Catalog UI Page
# --------------------------------------------------

@router.get(
    "/service-catalog-ui",
    response_class=HTMLResponse
)
def service_catalog_ui(
    request: Request,
    domain: str = "Vehicle"
):

    selected_domain = clean_csv_value(
        domain
    )

    if not selected_domain:

        selected_domain = "Vehicle"

    available_domains = load_available_domains()

    if not available_domains:

        available_domains = [
            "Vehicle"
        ]

    catalog_rows = load_service_catalog_rows_for_domain(
        selected_domain
    )

    groups_by_code = {}

    for row in catalog_rows:

        group_code = csv_int(
            row.get(
                "group_code"
            )
        )

        group_name = clean_csv_value(
            row.get(
                "group_name"
            )
        )

        service_code = csv_int(
            row.get(
                "service_code"
            )
        )

        service_item = clean_csv_value(
            row.get(
                "service_item"
            )
        )

        service_type_match = clean_csv_value(
            row.get(
                "service_type_match"
            )
        )

        service_category = clean_csv_value(
            row.get(
                "service_category"
            )
        )

        track_for_maintenance_due = clean_csv_value(
            row.get(
                "track_for_maintenance_due"
            )
        )

        if not group_name or not service_item:

            continue

        if group_code not in groups_by_code:

            groups_by_code[group_code] = {
                "group": {
                    "display_order": group_code,
                    "name": group_name
                },
                "items": []
            }

        groups_by_code[group_code]["items"].append(
            {
                "display_order": service_code,
                "item_name": service_item,
                "service_type_match": service_type_match,
                "service_category": service_category,
                "track_for_maintenance_due": track_for_maintenance_due
            }
        )

    catalog = []

    for group_code in sorted(
        groups_by_code.keys()
    ):

        group_entry = groups_by_code[
            group_code
        ]

        group_entry["items"].sort(
            key=lambda item: item["display_order"]
        )

        catalog.append(
            group_entry
        )

    return templates.TemplateResponse(
        request=request,
        name="service_catalog.html",
        context={
            "request": request,
            "catalog": catalog,
            "domain": selected_domain,
            "available_domains": available_domains
        }
    )