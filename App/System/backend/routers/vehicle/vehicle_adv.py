# --------------------------------------------------
# vehicle_adv.py
#
# Advanced Vehicle Information
#
# Purpose:
# - Keep advanced vehicle details separate from
#   the stable vehicle_ui.py router
# - Display acquisition and financial information
# - Load technical information from VINDecode.json
# --------------------------------------------------

import json
import os

from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from database import (
    SessionLocal
)

from models import (
    Vehicle
)

from helpers.storage import (
    get_vehicle_folder
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)
# --------------------------------------------------
# VIN Decode Display Filtering
# --------------------------------------------------

def is_meaningful_vin_value(
    value
) -> bool:
    """
    Return True when a VIN decode value contains
    meaningful information that should be displayed.

    Hide:
    - None
    - Blank text
    - Numeric zero
    - Text zero values
    - Not Applicable
    - N/A
    - NA
    - Unknown
    - Null

    Keep meaningful values such as:
    - No
    - Manual
    - Gasoline
    - 2
    - 2.9
    """

    if value is None:

        return False

    if isinstance(
        value,
        bool
    ):

        return True

    if isinstance(
        value,
        (
            int,
            float
        )
    ):

        return value != 0

    cleaned_value = str(
        value
    ).strip()

    if not cleaned_value:

        return False

    normalized_value = cleaned_value.lower()

    hidden_values = {
        "0",
        "0.0",
        "0.00",
        "n/a",
        "na",
        "not applicable",
        "unknown",
        "null",
        "none"
    }

    if normalized_value in hidden_values:

        return False

    return True


def build_vin_field_list(
    vin_decode: dict,
    field_definitions: list
) -> list:
    """
    Build a display-ready list of meaningful VIN fields.

    Each field definition should contain:

    key:
        The NHTSA VIN field name.

    label:
        The user-friendly display label.

    suffix:
        Optional text such as L or HP.
    """

    display_fields = []

    for field_definition in field_definitions:

        field_key = field_definition[
            "key"
        ]

        field_label = field_definition[
            "label"
        ]

        field_suffix = field_definition.get(
            "suffix",
            ""
        )

        value = vin_decode.get(
            field_key
        )

        if not is_meaningful_vin_value(
            value
        ):

            continue

        display_value = str(
            value
        ).strip()

        if field_suffix:

            display_value = (
                f"{display_value} "
                f"{field_suffix}"
            )

        display_fields.append(
            {
                "key": field_key,
                "label": field_label,
                "value": display_value
            }
        )

    return display_fields

# --------------------------------------------------
# Advanced Vehicle Information Page
# --------------------------------------------------

@router.get(
    "/vehicle/{vehicle_id}/advanced",
    response_class=HTMLResponse
)
def vehicle_advanced_information_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    if not vehicle:

        db.close()

        return RedirectResponse(
            url="/vehicles-ui",
            status_code=303
        )

    vehicle_folder = get_vehicle_folder(
        vehicle.id,
        vehicle.year,
        vehicle.make,
        vehicle.model
    )

    vin_json_path = os.path.join(
        vehicle_folder,
        "VINDecode.json"
    )

    vin_csv_path = os.path.join(
        vehicle_folder,
        "VINDecode.csv"
    )

    vin_decode_result = {}

    if os.path.exists(
        vin_json_path
    ):

        try:

            with open(
                vin_json_path,
                "r",
                encoding="utf-8"
            ) as file:

                vin_decode_data = json.load(
                    file
                )

            results = vin_decode_data.get(
                "Results",
                []
            )

            if results:

                vin_decode_result = results[0]

        except (
            OSError,
            json.JSONDecodeError
        ) as error:

            print(
                "Could not load VINDecode.json:",
                error
            )
    # ----------------------------------------------
    # Vehicle Identity Fields
    # ----------------------------------------------

    vehicle_identity_fields = build_vin_field_list(
        vin_decode_result,
        [
            {
                "key": "Manufacturer",
                "label": "Manufacturer"
            },
            {
                "key": "VehicleType",
                "label": "Vehicle Type"
            },
            {
                "key": "BodyClass",
                "label": "Body Class"
            },
            {
                "key": "Series",
                "label": "Series"
            },
            {
                "key": "Series2",
                "label": "Series 2"
            },
            {
                "key": "Doors",
                "label": "Doors"
            }
        ]
    )

    # ----------------------------------------------
    # Manufacturing Fields
    # ----------------------------------------------

    manufacturing_fields = build_vin_field_list(
        vin_decode_result,
        [
            {
                "key": "PlantCompanyName",
                "label": "Plant Company"
            },
            {
                "key": "PlantCity",
                "label": "Plant City"
            },
            {
                "key": "PlantState",
                "label": "Plant State"
            },
            {
                "key": "PlantCountry",
                "label": "Plant Country"
            }
        ]
    )

    # ----------------------------------------------
    # Engine Fields
    # ----------------------------------------------

    engine_fields = build_vin_field_list(
        vin_decode_result,
        [
            {
                "key": "EngineManufacturer",
                "label": "Engine Manufacturer"
            },
            {
                "key": "EngineModel",
                "label": "Engine Model"
            },
            {
                "key": "EngineConfiguration",
                "label": "Engine Configuration"
            },
            {
                "key": "EngineCylinders",
                "label": "Engine Cylinders"
            },
            {
                "key": "DisplacementL",
                "label": "Displacement",
                "suffix": "L"
            },
            {
                "key": "FuelTypePrimary",
                "label": "Primary Fuel Type"
            },
            {
                "key": "FuelTypeSecondary",
                "label": "Secondary Fuel Type"
            },
            {
                "key": "FuelInjectionType",
                "label": "Fuel Injection Type"
            },
            {
                "key": "EngineHP",
                "label": "Engine Horsepower",
                "suffix": "HP"
            },
            {
                "key": "Turbo",
                "label": "Turbo"
            },
            {
                "key": "ElectrificationLevel",
                "label": "Electrification Level"
            }
        ]
    )

    # ----------------------------------------------
    # Transmission and Drivetrain Fields
    # ----------------------------------------------

    transmission_fields = build_vin_field_list(
        vin_decode_result,
        [
            {
                "key": "TransmissionStyle",
                "label": "Transmission Style"
            },
            {
                "key": "TransmissionSpeeds",
                "label": "Transmission Speeds"
            },
            {
                "key": "DriveType",
                "label": "Drive Type"
            },
            {
                "key": "Axles",
                "label": "Axles"
            },
            {
                "key": "AxleConfiguration",
                "label": "Axle Configuration"
            }
        ]
    )

    # ----------------------------------------------
    # Safety and Equipment Fields
    # ----------------------------------------------

    safety_fields = build_vin_field_list(
        vin_decode_result,
        [
            {
                "key": "ABS",
                "label": "Anti-Lock Brakes"
            },
            {
                "key": "ESC",
                "label": "Electronic Stability Control"
            },
            {
                "key": "TractionControl",
                "label": "Traction Control"
            },
            {
                "key": "TPMS",
                "label": "Tire Pressure Monitoring System"
            },
            {
                "key": "SeatBeltsAll",
                "label": "Seat Belt Type"
            },
            {
                "key": "BackupCamera",
                "label": "Backup Camera"
            },
            {
                "key": "ForwardCollisionWarning",
                "label": "Forward Collision Warning"
            },
            {
                "key": "LaneDepartureWarning",
                "label": "Lane Departure Warning"
            },
            {
                "key": "AdaptiveCruiseControl",
                "label": "Adaptive Cruise Control"
            }
        ]
    )

    vin_json_exists = os.path.exists(
        vin_json_path
    )

    vin_csv_exists = os.path.exists(
        vin_csv_path
    )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle/vehicle_advanced.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "vin_decode": vin_decode_result,
            "vehicle_identity_fields": vehicle_identity_fields,
            "manufacturing_fields": manufacturing_fields,
            "engine_fields": engine_fields,
            "transmission_fields": transmission_fields,
            "safety_fields": safety_fields,
            "vin_json_exists": vin_json_exists,
            "vin_csv_exists": vin_csv_exists
        }
    )