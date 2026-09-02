from __future__ import annotations

import requests
from typing import Any, Dict, List, Optional


class AddressLookupService:
    """Service layer for address -> parcel lookup using Sarasota County ArcGIS REST API.

    This keeps the House domain isolated from vehicle logic while mirroring
    the project structure the vehicle app uses.
    """

    # Sarasota County ArcGIS REST endpoint
    SARASOTA_REST_URL = (
        "https://services3.arcgis.com/icrWMv7eBkctFu1f/arcgis/rest/services/"
        "ParcelHosted/FeatureServer/0/query"
    )

    def normalize_address(self, payload: Dict[str, Any]) -> Dict[str, str]:
        street = str(payload.get("street", "")).strip()
        city = str(payload.get("city", "")).strip()
        state = str(payload.get("state", "")).strip().upper()
        zip_code = str(payload.get("zip_code", "")).strip()

        return {
            "street": street,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "country": "US",
        }

    def geocode_address(self, normalized: Dict[str, str]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "formatted_address": f"{normalized['street']}, {normalized['city']}, {normalized['state']} {normalized['zip_code']}",
            "state": normalized["state"],
            "zip_code": normalized["zip_code"],
            "country": normalized["country"],
            "latitude": None,
            "longitude": None,
            "county": None,
        }

    def lookup_parcel_details(self, normalized: Dict[str, str]) -> Dict[str, Any]:
        """Query Sarasota County ArcGIS REST API by street address."""
        try:
            # Search by street address (LOCS field in Sarasota County)
            query_params = {
                "where": f"UPPER(LOCS) LIKE UPPER('%{normalized['street']}%')",
                "outFields": [
                    "ACCOUNT",  # Parcel ID
                    "NAME1",    # Owner name
                    "LOCS",     # Address
                    "DWELL_UNIT",  # Property type indicator
                    "LAND_USE_CODE",  # Land use
                    "AC_DECLAND",  # Assessed value
                ],
                "returnGeometry": False,
                "f": "json",
            }

            response = requests.get(
                self.SARASOTA_REST_URL,
                params=query_params,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            features = data.get("features", [])

            if not features:
                return {
                    "source": "sarasota-county-arcgis",
                    "parcel_id": None,
                    "county": "Sarasota",
                    "owner": None,
                    "land_use": None,
                    "tax_assessed_value": None,
                    "legal_description": None,
                    "raw": {},
                    "status": "not_found",
                    "message": f"No parcels found for address: {normalized['street']}",
                }

            # Return first matching parcel
            feature = features[0]
            attrs = feature.get("attributes", {})

            return {
                "source": "sarasota-county-arcgis",
                "parcel_id": attrs.get("ACCOUNT"),
                "county": "Sarasota",
                "owner": attrs.get("NAME1"),
                "land_use": attrs.get("LAND_USE_CODE"),
                "tax_assessed_value": attrs.get("AC_DECLAND"),
                "legal_description": attrs.get("LOCS"),
                "raw": attrs,
                "status": "found",
                "message": "Parcel details retrieved successfully.",
            }

        except requests.exceptions.RequestException as e:
            return {
                "source": "sarasota-county-arcgis",
                "parcel_id": None,
                "county": "Sarasota",
                "owner": None,
                "land_use": None,
                "tax_assessed_value": None,
                "legal_description": None,
                "raw": {},
                "status": "error",
                "message": f"API error: {str(e)}",
            }
        except Exception as e:
            return {
                "source": "sarasota-county-arcgis",
                "parcel_id": None,
                "county": "Sarasota",
                "owner": None,
                "land_use": None,
                "tax_assessed_value": None,
                "legal_description": None,
                "raw": {},
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
            }

    def lookup_address(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self.normalize_address(payload)
        geocode = self.geocode_address(normalized)
        parcel = self.lookup_parcel_details(normalized)

        return {
            "address": normalized,
            "geocode": geocode,
            "parcel": parcel,
            "provider": "house-address-lookup-test",
            "success": parcel.get("status") == "ok",
        }
