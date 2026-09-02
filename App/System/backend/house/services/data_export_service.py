"""Service for exporting house property lookup data to JSON and CSV files."""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class HouseDataExportService:
    """Export house property lookup results to JSON and CSV files."""

    def __init__(self, data_folder: str = None):
        """Initialize with a data folder path.
        
        Args:
            data_folder: Base folder for storing house data. 
                        Defaults to YourDataFolder/House/
        """
        if data_folder is None:
            # Use absolute path directly - adjust based on actual structure
            data_folder = Path("C:/MaintainHub/YourDataFolder/House").resolve()
        else:
            data_folder = Path(data_folder)
        
        self.base_folder = Path(data_folder)
        self.base_folder.mkdir(parents=True, exist_ok=True)

    def _get_house_folder(self, house_data: Dict[str, Any]) -> Path:
        """Create a folder for the house based on its address and ID.
        
        Args:
            house_data: Dictionary with house information including 'id' and 'address'
        
        Returns:
            Path to the house's folder
        """
        address = house_data.get("address", "Unknown").replace(" ", "_").replace("/", "_")
        house_id = house_data.get("id", "unknown")
        folder_name = f"{house_id}_{address}"
        house_folder = self.base_folder / folder_name
        house_folder.mkdir(parents=True, exist_ok=True)
        return house_folder

    def save_lookup_data(self, house_data: Dict[str, Any], lookup_result: Dict[str, Any]) -> Dict[str, str]:
        """Save lookup result to JSON and CSV files.
        
        Args:
            house_data: Dictionary with house information
            lookup_result: Dictionary with lookup result from address service
        
        Returns:
            Dictionary with paths to saved files
        """
        house_folder = self._get_house_folder(house_data)
        
        # Save JSON
        json_path = house_folder / "PropertyLookup.json"
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "house_id": house_data.get("id"),
            "address": house_data.get("address"),
            "city": house_data.get("city"),
            "county": house_data.get("county"),
            "state": house_data.get("state"),
            "zip_code": house_data.get("zip_code"),
            "lookup_result": lookup_result,
            "parcel_data": lookup_result.get("parcel", {}),
        }
        
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)

        # Save CSV
        csv_path = house_folder / "PropertyLookup.csv"
        
        # Flatten the data for CSV
        parcel = lookup_result.get("parcel", {})
        csv_data = [
            ["Field", "Value"],
            ["Timestamp", json_data["timestamp"]],
            ["House ID", house_data.get("id", "")],
            ["Address", house_data.get("address", "")],
            ["City", house_data.get("city", "")],
            ["County", house_data.get("county", "")],
            ["State", house_data.get("state", "")],
            ["ZIP Code", house_data.get("zip_code", "")],
            ["Property Type", house_data.get("property_type", "")],
            ["Bedrooms", str(house_data.get("bedrooms", ""))],
            ["Bathrooms", str(house_data.get("bathrooms", ""))],
            ["", ""],
            ["--- Lookup Results ---", ""],
            ["Source", parcel.get("source", "")],
            ["Status", parcel.get("status", "")],
            ["Message", parcel.get("message", "")],
            ["Parcel ID", parcel.get("parcel_id", "")],
            ["Owner", parcel.get("owner", "")],
            ["Land Use", parcel.get("land_use", "")],
            ["Tax Assessed Value", str(parcel.get("tax_assessed_value", ""))],
            ["Legal Description", parcel.get("legal_description", "")],
        ]
        
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)

        return {
            "json": str(json_path),
            "csv": str(csv_path),
            "house_folder": str(house_folder),
        }

    def save_house_info(self, house_data: Dict[str, Any]) -> Dict[str, str]:
        """Save basic house information to HouseInfo.txt.
        
        Args:
            house_data: Dictionary with house information
        
        Returns:
            Dictionary with path to saved file
        """
        house_folder = self._get_house_folder(house_data)
        
        info_path = house_folder / "HouseInfo.txt"
        
        lines = [
            f"House ID: {house_data.get('id', '')}",
            f"Address: {house_data.get('address', '')}",
            f"City: {house_data.get('city', '')}",
            f"County: {house_data.get('county', '')}",
            f"State: {house_data.get('state', '')}",
            f"ZIP Code: {house_data.get('zip_code', '')}",
            f"Property Type: {house_data.get('property_type', '')}",
            f"Bedrooms: {house_data.get('bedrooms', '')}",
            f"Bathrooms: {house_data.get('bathrooms', '')}",
            f"Date Added: {datetime.now().isoformat()}",
        ]
        
        with open(info_path, "w") as f:
            f.write("\n".join(lines))

        return {"house_info": str(info_path)}
