# vendor.py
# schemas/vendor.py
from pydantic import BaseModel


class VendorCreate(BaseModel):

    name: str

    vendor_type: str

    address_1: str = ""
    address_2: str = ""

    city: str = ""
    state: str = ""
    zip_code: str = ""

    phone: str = ""
    email: str = ""

    website: str = ""

    primary_contact: str = ""

    notes: str = ""

    is_preferred: bool = False