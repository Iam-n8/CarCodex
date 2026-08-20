# helpers/storage.py

import os
import re
import json
import csv

from helpers.app_paths import (
    get_vehicle_data_folder
)

# --------------------------------------------------
# Safe File/Folder Naming
# --------------------------------------------------

def safe_name(value: str) -> str:
    """
    Convert a display name into a safe folder name.

    Example:
        Corvette Blue
        ->
        Corvette_Blue
    """

    if not value:
        return "Unnamed"

    return re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        value.strip()
    )

# --------------------------------------------------
# Vehicle Folder
# --------------------------------------------------

def get_vehicle_folder(
    vehicle_id: int,
    year: int,
    make: str,
    model: str
) -> str:

    vehicle_folder = (
        f"{year}_"
        f"{safe_name(make)}_"
        f"{safe_name(model)}_"
        f"V{vehicle_id}"
    )

    return os.path.join(
        str(
            get_vehicle_data_folder()
        ),
        vehicle_folder
    )

# --------------------------------------------------
# Create Vehicle Structure
# --------------------------------------------------

def create_vehicle_folders(
    vehicle
) -> str:

    base_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.year,
        vehicle.make,
        vehicle.model
    )

    folders = [

        # Main Categories

        "Documents",
        "Maintenance",
        "Photos",
        "Exports",

        # Document Categories

        "Documents/Registration",
        "Documents/Insurance",
        "Documents/Warranty",
        "Documents/Purchase",
        "Documents/Manual",
        "Documents/Inspection",
        "Documents/Receipts",
        "Documents/Other",

        # Maintenance

        "Maintenance/Other"
    ]

    os.makedirs(
        base_folder,
        exist_ok=True
    )

    for folder in folders:

        os.makedirs(
            os.path.join(
                base_folder,
                folder
            ),
            exist_ok=True
        )
    
    create_vehicle_info_file(
        vehicle
    )
    return base_folder

# --------------------------------------------------
# Vehicle Info File
# --------------------------------------------------

def create_vehicle_info_file(
    vehicle
):

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.year,
        vehicle.make,
        vehicle.model
    )
    os.makedirs(
        vehicle_folder,
        exist_ok=True
    )
    info_file = os.path.join(
        vehicle_folder,
        "VehicleInfo.txt"
    )

    with open(
        info_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
    f"""CarCodex Vehicle Information

Vehicle ID: {vehicle.id}

Nickname: {vehicle.nickname}

Year: {vehicle.year}
Make: {vehicle.make}
Model: {vehicle.model}
Trim: {vehicle.trim}

VIN: {vehicle.vin}

Current Mileage: {vehicle.current_mileage}
"""
        )

    return info_file

# --------------------------------------------------
# Document Filename
# --------------------------------------------------

def build_document_filename(
    document_type: str,
    document_date: str,
    document_id: int,
    extension: str
) -> str:
    """
    Example:

    Registration-2026-04-01-D442.pdf
    """

    return (
        f"{safe_name(document_type)}"
        f"-{document_date}"
        f"-D{document_id}"
        f".{extension.lower()}"
    )

# --------------------------------------------------
# Document Folder
# --------------------------------------------------

def get_document_folder(
    vehicle,
    document_type: str
) -> str:
    
    ''' Returns the folder path for a specific document type within a vehicle's directory. '''

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.year,
        vehicle.make,
        vehicle.model
    )

    document_folder = os.path.join(
        vehicle_folder,
        "Documents",
        safe_name(document_type)
    )

    os.makedirs(
        document_folder,
        exist_ok=True
    )
    create_vehicle_info_file(
        vehicle
    )
    return document_folder

# --------------------------------------------------
# Full Document Path
# --------------------------------------------------

def build_document_path(
    vehicle,
    document_type: str,
    document_date: str,
    document_id: int,
    extension: str
) -> str:
    """
    Example:

    CarCodex_Data/
        Vehicles/
            2008_Chevrolet_Corvette_V17/
                Documents/
                    Insurance/
                        Insurance-2026-08-01-D443.pdf
    """

    folder = get_document_folder(
        vehicle,
        document_type
    )

    filename = build_document_filename(
        document_type,
        document_date,
        document_id,
        extension
    )

    return os.path.join(
        folder,
        filename
    )

# --------------------------------------------------
# Save Document File
# --------------------------------------------------

def save_document_file(
    vehicle,
    document_type: str,
    document_date: str,
    document_id: int,
    uploaded_file
):
    """
    Save an uploaded file using the
    CarCodex storage convention.
    """

    extension = uploaded_file.filename.split(
        "."
    )[-1]

    destination = build_document_path(
        vehicle,
        document_type,
        document_date,
        document_id,
        extension
    )

    with open(
        destination,
        "wb"
    ) as buffer:

        buffer.write(
            uploaded_file.file.read()
        )

    return destination

# --------------------------------------------------
# Maintenance Folder
# --------------------------------------------------

def get_maintenance_folder(
    vehicle,
    visit,
    primary_reason: str
) -> str:

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.year,
        vehicle.make,
        vehicle.model
    )

    folder_name = (
        f"{visit.visit_date}-"
        f"{safe_name(primary_reason)}-"
        f"M{visit.id}"
    )

    maintenance_folder = os.path.join(
        vehicle_folder,
        "Maintenance",
        folder_name
    )

    os.makedirs(
        maintenance_folder,
        exist_ok=True
    )

    return maintenance_folder
# --------------------------------------------------
# VIN Decode Export Files
# --------------------------------------------------

def get_vin_decode_json_path(
    vehicle
) -> str:
    """
    Return the VINDecode.json path for a vehicle.
    """

    vehicle_folder = create_vehicle_folders(
        vehicle
    )

    return os.path.join(
        vehicle_folder,
        "VINDecode.json"
    )


def get_vin_decode_csv_path(
    vehicle
) -> str:
    """
    Return the VINDecode.csv path for a vehicle.
    """

    vehicle_folder = create_vehicle_folders(
        vehicle
    )

    return os.path.join(
        vehicle_folder,
        "VINDecode.csv"
    )


def save_vin_decode_json(
    vehicle,
    decode_data
):
    """
    Save the complete NHTSA VIN decode response
    as VINDecode.json in the vehicle folder.
    """

    json_path = get_vin_decode_json_path(
        vehicle
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            decode_data,
            file,
            indent=4
        )

    return json_path


def save_vin_decode_csv(
    vehicle,
    decode_data
):
    """
    Save the NHTSA VIN decode response as a
    human-readable VINDecode.csv file.
    """

    csv_path = get_vin_decode_csv_path(
        vehicle
    )

    result = {}

    if decode_data.get("Results"):

        result = decode_data["Results"][0]

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "Field",
                "Value"
            ]
        )

        writer.writerow(
            [
                "Count",
                decode_data.get(
                    "Count",
                    ""
                )
            ]
        )

        writer.writerow(
            [
                "Message",
                decode_data.get(
                    "Message",
                    ""
                )
            ]
        )

        writer.writerow(
            [
                "SearchCriteria",
                decode_data.get(
                    "SearchCriteria",
                    ""
                )
            ]
        )
        for field_name in sorted(
            result.keys()
        ):

            writer.writerow(
                [
                    field_name,
                    result.get(
                        field_name,
                        ""
                    )
                ]
            )

    return csv_path
def save_vin_decode_files(
    vehicle,
    decode_data
):
    """
    Save both VINDecode.json and VINDecode.csv
    for a vehicle.
    """

    json_path = save_vin_decode_json(
        vehicle,
        decode_data
    )

    csv_path = save_vin_decode_csv(
        vehicle,
        decode_data
    )

    return {
        "json_path": json_path,
        "csv_path": csv_path
    }