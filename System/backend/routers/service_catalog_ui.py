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

import os
import csv


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

from fastapi.templating import (
    Jinja2Templates
)
from helpers.service_catalog_loader import (
    load_vehicle_service_catalog_rows,
    clean_csv_value,
    csv_int
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# Service Catalog CSV
# --------------------------------------------------


# --------------------------------------------------
# Seed Default Service Catalog
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

        notes = clean_csv_value(
            row.get(
                "notes"
            )
        )

        if not group_name or not service_item:

            continue

        if not service_type_match:

            service_type_match = service_item

        if group_code not in groups_by_code:

            group = ServiceGroup(

                name=group_name,

                display_order=group_code,

                inactive=False

            )

            db.add(
                group
            )

            db.commit()

            db.refresh(
                group
            )

            groups_by_code[group_code] = group

            groups_created += 1

        group = groups_by_code[
            group_code
        ]

        item = ServiceItem(

            group_id=group.id,

            item_name=service_item,

            service_type_match=service_type_match,

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
# List Service Catalog JSON
# --------------------------------------------------

@router.get(
    "/service-catalog"
)
def get_service_catalog():

    db = SessionLocal()

    groups = db.query(
        ServiceGroup
    ).filter(
        ServiceGroup.inactive == False
    ).order_by(
        ServiceGroup.display_order
    ).all()

    results = []

    for group in groups:

        items = db.query(
            ServiceItem
        ).filter(
            ServiceItem.group_id == group.id,
            ServiceItem.inactive == False
        ).order_by(
            ServiceItem.display_order
        ).all()

        results.append(
            {
                "id": group.id,
                "name": group.name,
                "display_order": group.display_order,
                "items": [
                    {
                        "id": item.id,
                        "item_name": item.item_name,
                        "service_type_match": item.service_type_match,
                        "display_order": item.display_order
                    }
                    for item in items
                ]
            }
        )

    db.close()

    return results
# --------------------------------------------------
# Service Catalog UI Page
# --------------------------------------------------

@router.get(
    "/service-catalog-ui",
    response_class=HTMLResponse
)
def service_catalog_ui(
    request: Request
):

    db = SessionLocal()

    groups = db.query(
        ServiceGroup
    ).filter(
        ServiceGroup.inactive == False
    ).order_by(
        ServiceGroup.display_order
    ).all()

    catalog = []

    for group in groups:

        items = db.query(
            ServiceItem
        ).filter(
            ServiceItem.group_id == group.id,
            ServiceItem.inactive == False
        ).order_by(
            ServiceItem.display_order
        ).all()

        catalog.append(
            {
                "group": group,
                "items": items
            }
        )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="service_catalog.html",
        context={
            "request": request,
            "catalog": catalog
        }
    )

