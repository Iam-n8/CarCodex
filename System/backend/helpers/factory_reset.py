# --------------------------------------------------
# factory_reset.py
#
# Factory Reset Helper
#
# Purpose:
# - Clear all CarCodex user data
# - Clear generated data folders
# - Preserve reference files such as ServiceCatalog.csv
# - Seed a known development baseline
# --------------------------------------------------

import os
import shutil

from database import (
    SessionLocal
)

from models import (
    Vehicle,
    Vendor,
    MaintenanceVisit,
    MaintenanceSchedule,
    Document,
    ServiceRecord,
    ServiceGroup,
    ServiceItem
)

from helpers.storage import (
    create_vehicle_folders,
    create_vehicle_info_file
)

from helpers.service_catalog_loader import (
    load_vehicle_service_catalog_rows,
    load_maintenance_trackable_rows,
    clean_csv_value,
    csv_int,
    csv_bool
)
from helpers.app_paths import (
    get_vehicle_data_folder
)


# --------------------------------------------------
# Clear Generated Folders
# --------------------------------------------------

def clear_generated_folders():
    """
    Delete generated user data folders.

    Important:
    This does NOT delete ServiceCatalog.csv.
    """

    vehicles_folder = get_vehicle_data_folder()

    if vehicles_folder.exists():

        shutil.rmtree(
            vehicles_folder
        )

    vehicles_folder.mkdir(
        parents=True,
        exist_ok=True
    )


# --------------------------------------------------
# Clear Database Tables
# --------------------------------------------------

def clear_database_data():
    """
    Clear user/application data from database tables.

    This is intended for development reset.
    """

    db = SessionLocal()

    # Child/detail tables first
    db.query(
        Document
    ).delete()

    db.query(
        ServiceRecord
    ).delete()

    db.query(
        MaintenanceVisit
    ).delete()

    db.query(
        MaintenanceSchedule
    ).delete()

    # Vehicles and vendors
    db.query(
        Vehicle
    ).delete()

    db.query(
        Vendor
    ).delete()

    # Service catalog database copy
    db.query(
        ServiceItem
    ).delete()

    db.query(
        ServiceGroup
    ).delete()

    db.commit()

    db.close()


# --------------------------------------------------
# Seed Service Catalog
# --------------------------------------------------

def seed_service_catalog():
    """
    Seed ServiceGroup and ServiceItem rows from
    ServiceCatalog.csv for the Vehicle domain.

    All catalog metadata is written directly so
    Factory Reset does not depend on an old migration
    running again.
    """

    db = SessionLocal()

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
        "groups_created": groups_created,
        "items_created": items_created
    }


# --------------------------------------------------
# Seed Default Vendor
# --------------------------------------------------

def seed_default_vendor():
    """
    Seed default vendor:
    My Garage
    """

    db = SessionLocal()

    vendor = Vendor(

        name="My Garage",

        address_1="",

        phone="",

        website="",

        notes="Default seeded vendor."

    )

    db.add(
        vendor
    )

    db.commit()

    db.refresh(
        vendor
    )

    vendor_id = vendor.id

    db.close()

    return vendor_id


# --------------------------------------------------
# Seed Test Vehicle
# --------------------------------------------------

def seed_test_vehicle():
    """
    Seed test vehicle:

    1982 FERRARI 308GTSi
    VIN: ZFFAA02A1C0039757
    """

    db = SessionLocal()

    vehicle = Vehicle(

        nickname="Test Ferrari",

        year=1982,

        make="FERRARI",

        model="308GTSi",

        trim="Trim Unknown",

        vin="ZFFAA02A1C0039757",

        current_mileage=0

    )

    db.add(
        vehicle
    )

    db.commit()

    db.refresh(
        vehicle
    )

    vehicle_id = vehicle.id

    create_vehicle_folders(
        vehicle
    )

    create_vehicle_info_file(
        vehicle
    )

    db.close()

    return vehicle_id

# --------------------------------------------------
# Seed MaintSch For Vehicle
# --------------------------------------------------

def seed_maintenance_schedule_for_vehicle(
    vehicle_id: int
):
    """
    Seed MaintenanceSchedule rows from ServiceCatalog.csv.

    Uses only rows where:
    domain = Vehicle
    track_for_maintenance_due = yes
    """

    db = SessionLocal()

    catalog_rows = load_maintenance_trackable_rows()

    items_created = 0

    for row in catalog_rows:

        item_name = clean_csv_value(
            row.get(
                "service_item"
            )
        )

        service_type_match = clean_csv_value(
            row.get(
                "service_type_match"
            )
        )

        miles_interval = csv_int(
            row.get(
                "default_miles_interval"
            ),
            default=0
        )

        period_months = csv_int(
            row.get(
                "default_period_months"
            ),
            default=0
        )

        display_order = csv_int(
            row.get(
                "service_code"
            ),
            default=0
        )

        notes = clean_csv_value(
            row.get(
                "notes"
            )
        )

        if not item_name:

            continue

        if not service_type_match:

            service_type_match = item_name

        if miles_interval == 0:

            miles_interval = None

        if period_months == 0:

            period_months = None

        schedule = MaintenanceSchedule(

            vehicle_id=vehicle_id,

            item_name=item_name,

            service_type_match=service_type_match,

            miles_interval=miles_interval,

            period_months=period_months,

            inactive=False,

            notes=notes,

            display_order=display_order

        )

        db.add(
            schedule
        )

        items_created += 1

    db.commit()

    db.close()

    return items_created
# --------------------------------------------------
# Run Factory Reset
# --------------------------------------------------

def run_factory_reset():
    """
    Run full Factory Reset with seed data.

    This deletes all database data and generated folders,
    then recreates the development baseline.
    """

    clear_generated_folders()

    clear_database_data()

    catalog_result = seed_service_catalog()

    vendor_id = seed_default_vendor()

    vehicle_id = seed_test_vehicle()

    maintsch_items_created = seed_maintenance_schedule_for_vehicle(
        vehicle_id
    )

    return {
        "message": "Factory reset complete",
        "catalog": catalog_result,
        "vendor_id": vendor_id,
        "vehicle_id": vehicle_id,
        "maintsch_items_created": maintsch_items_created
    }