import os


def create_vehicle_folders(vehicle_id):

    base_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Documents",
            f"VEH_{vehicle_id:06d}"
        )
    )

    folders = [
        "Maintenance",
        "Repairs",
        "Mods",
        "Insurance",
        "Registration",
        "Tires",
        "Events",
        "Photos",
        "Warranty",
        "Reports",
        "Misc"
    ]

    os.makedirs(base_folder, exist_ok=True)

    for folder in folders:
        os.makedirs(
            os.path.join(base_folder, folder),
            exist_ok=True
        )