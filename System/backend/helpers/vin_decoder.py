# helpers/vin_decoder.py

import requests


def decode_vin(vin: str):

    url = (
        f"https://vpic.nhtsa.dot.gov/api/"
        f"vehicles/DecodeVinValues/"
        f"{vin}?format=json"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("Results"):
        return None

    return data



