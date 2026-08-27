# Cars.py 

import csv
import requests

# Fetch all vehicle makes from the official NHTSA database
url = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
response = requests.get(url).json()
makes = response.get("Results", [])

print(f"Retrieved {len(makes)} makes. Processing models for recent years...")

# Example structure to write your own CSV
with open("us_cars_last_10_years.csv", mode="w", newline="", encoding="utf-8") as f:
  writer = csv.writer(f)
  writer.writerow(["Year", "Make", "Model"])

  # Loop through a sample or all makes to extract models
  # (NHTSA endpoint allows querying models for specific makes and years)