# helpers/storage.py

import os
import re






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
    nickname: str
) -> str:
    """
    Example:

    CarCodex_Data/
        Vehicles/
            Corvette_Blue_V17/
    """

    vehicle_folder = (
        f"{safe_name(nickname)}_V{vehicle_id}"
    )

    return os.path.join(
        "CarCodex_Data",
        "Vehicles",
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
# Vehicle Info File
# --------------------------------------------------

def create_vehicle_info_file(
    vehicle
):

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.nickname
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
def get_document_folder(
    vehicle,
    document_type: str
):
    pass