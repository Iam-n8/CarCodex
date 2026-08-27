# --------------------------------------------------
# storage.py
#
# Maintain Hub Storage Utilities
#
# Purpose:
# - Centralize vehicle file storage
# - Create vehicle folder structures
# - Generate safe file and folder names
# - Manage document storage locations
# - Manage VIN decode file locations
#
# Notes:
#
# Vehicle data is stored under:
#
#   MaintainHub/
#   └── YourDataFolder/
#       └── Vehicles/
#           └── <Vehicle Folder>
#
# Examples:
#
#   2021_CHEVROLET_Corvette_V6
#   2019_LAND_ROVER_Discovery_Sport_V7
#
# The root vehicle path is obtained from:
#
#   helpers.app_paths.get_vehicle_data_folder()
#
# Never hardcode storage locations.
# Always use app_paths.py.
# --------------------------------------------------

import os
import re

from helpers.app_paths import (
    get_vehicle_data_folder
)


# --------------------------------------------------
# Safe File/Folder Naming
# --------------------------------------------------

def safe_name(value: str) -> str:
    """
    Convert a display name into a safe
    file-system friendly name.

    Example:

        Corvette Blue

    becomes

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
    nickname: str
) -> str:
    """
    Return the full vehicle folder path.

    Example:

    MaintainHub/
    └── YourDataFolder/
        └── Vehicles/
            └── Corvette_Blue_V17
    """

    vehicle_folder = (
        f"{safe_name(nickname)}_V{vehicle_id}"
    )

    return os.path.join(
        str(get_vehicle_data_folder()),
        vehicle_folder
    )


# --------------------------------------------------
# Create Vehicle Structure
# --------------------------------------------------

def create_vehicle_folders(
    vehicle_id: int,
    nickname: str
) -> str:

    base_folder = get_vehicle_folder(
        vehicle_id,
        nickname
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

    return base_folder


# --------------------------------------------------
# Vehicle Information File
# --------------------------------------------------

def create_vehicle_info_file(
    vehicle
):
    """
    Create or refresh VehicleInfo.txt.
    """

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.nickname
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
f"""Maintain Hub Vehicle Information

Vehicle ID: {vehicle.id}

Nickname: {vehicle.nickname}

Year: {vehicle.year}
Make: {vehicle.make}
Model: {vehicle.model}
Trim: {vehicle.trim}

VIN: {vehicle.vin}

Current Mileage: {vehicle.current_mileage}

Related Files:

VINDecode.json
VINDecode.csv
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
    """
    Return the folder used to store a
    document category for a vehicle.
    """

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.nickname
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

    return document_folder