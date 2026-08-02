# vendor_ui.py

from fastapi import (
    APIRouter,
    Request,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from database import SessionLocal

from models import (
    Vendor
)

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)




# --------------------------------------------------
# Vendor Detail
# --------------------------------------------------

@router.get(
    "/vendor/{vendor_id}",
    response_class=HTMLResponse
)
def vendor_detail(
    request: Request,
    vendor_id: int
):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendor_detail.html",
        context={
            "request": request,
            "vendor": vendor
        }
    )
# --------------------------------------------------
# Edit Vendor Page
# --------------------------------------------------

@router.get(
    "/vendor-edit/{vendor_id}",
    response_class=HTMLResponse
)
def vendor_edit_page(
    request: Request,
    vendor_id: int
):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendor_edit.html",
        context={
            "request": request,
            "vendor": vendor
        }
    )
# --------------------------------------------------
# Edit Vendor Submit
# --------------------------------------------------

@router.post(
    "/vendor-edit/{vendor_id}"
)
def vendor_edit_submit(

    vendor_id: int,

    name: str = Form(...),

    address_1: str = Form(""),

    phone: str = Form(""),

    website: str = Form(""),

    notes: str = Form("")

):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    vendor.name = name
    vendor.address_1 = address_1
    vendor.phone = phone
    vendor.website = website
    vendor.notes = notes

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/vendor/{vendor_id}",
        status_code=303
    )
