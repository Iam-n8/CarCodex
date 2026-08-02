# Vehicle UI Routes
import os


from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File
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
    Vehicle,
    MaintenanceVisit,
    MaintenanceSchedule,
    Document,
    Vendor,
    ServiceType,
    ServiceRecord   
)

from helpers.storage import (
    create_vehicle_folders,
    create_vehicle_info_file,
    get_maintenance_folder
    )


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)
@router.get(
    "/vehicles-ui",
    response_class=HTMLResponse
)
def vehicles_ui(
    request: Request
):

    db = SessionLocal()

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == False
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicles.html",
        context={
            "request": request,
            "vehicles": vehicles
        }
    )
@router.get(
    "/vehicle/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_detail(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    visits = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.vehicle_id == vehicle_id
    ).all()

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).all()
    documents = db.query(
        Document
    ).filter(
        Document.vehicle_id == vehicle_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_detail.html",

        context={
            "request": request,
            "vehicle": vehicle,
            "visits": visits,

            "schedules": schedules,

            "visit_count": len(visits),

            "document_count": len(documents),

            "vendor_count": 0
        }       
    )
# --------------------------------------------------
# Add Vehicle Page
# --------------------------------------------------

@router.get(
    "/vehicle-add",
    response_class=HTMLResponse
)
def vehicle_add_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="vehicle_add.html",
        context={
            "request": request
        }
    )
# --------------------------------------------------
# Add Vehicle Submit
# --------------------------------------------------

@router.post(
    "/vehicle-add"
)
def vehicle_add_submit(

    nickname: str = Form(...),

    year: int = Form(...),

    make: str = Form(...),

    model: str = Form(...),

    trim: str = Form(...),

    vin: str = Form(...),

    current_mileage: int = Form(...)

):

    db = SessionLocal()

    vehicle = Vehicle(

        nickname=nickname,

        year=year,

        make=make,

        model=model,

        trim=trim,

        vin=vin,

        current_mileage=current_mileage

    )

    db.add(vehicle)

    db.commit()

    db.refresh(vehicle)

    create_vehicle_folders(
        vehicle
    )

    db.close()

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )
# --------------------------------------------------
# Edit Vehicle Page
# --------------------------------------------------

@router.get(
    "/vehicle-edit/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_edit_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_edit.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Edit Vehicle Submit
# --------------------------------------------------

@router.post(
    "/vehicle-edit/{vehicle_id}"
)
def vehicle_edit_submit(

    vehicle_id: int,

    nickname: str = Form(...),

    year: int = Form(...),

    make: str = Form(...),

    model: str = Form(...),

    trim: str = Form(...),

    vin: str = Form(...),

    current_mileage: int = Form(...)

):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vehicle.nickname = nickname
    vehicle.year = year
    vehicle.make = make
    vehicle.model = model
    vehicle.trim = trim
    vehicle.vin = vin
    vehicle.current_mileage = current_mileage

    db.commit()

    create_vehicle_info_file(
        vehicle
    )

    db.close()

    return RedirectResponse(
        url=f"/vehicle/{vehicle_id}",
        status_code=303
    )

# --------------------------------------------------
# Archive Vehicle Page
# --------------------------------------------------

@router.get(
    "/vehicle-archive/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_archive_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_archive.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Archive Vehicle Submit
# --------------------------------------------------

@router.post(
    "/vehicle-archive/{vehicle_id}"
)
def vehicle_archive_submit(
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vehicle.archived = True

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )

# --------------------------------------------------
# Restore Vehicle Page
# --------------------------------------------------

@router.get(
    "/vehicle-restore/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_restore_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_restore.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
@router.post(
    "/vehicle-restore/{vehicle_id}"
)
def vehicle_restore_submit(
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vehicle.archived = False

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )
@router.get(
    "/vendors-ui",
    response_class=HTMLResponse
)
def vendors_ui(
    request: Request
):

    db = SessionLocal()

    vendors = db.query(
        Vendor
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendors.html",
        context={
            "request": request,
            "vendors": vendors
        }
    )
@router.get(
    "/vendor-add",
    response_class=HTMLResponse
)
def vendor_add_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="vendor_add.html",
        context={
            "request": request
        }
    )
@router.post(
    "/vendor-add"
)
def vendor_add_submit(

    name: str = Form(...),

    address_1: str = Form(""),

    phone: str = Form(""),

    website: str = Form(""),

    notes: str = Form("")

):

    db = SessionLocal()

    vendor = Vendor(

        name=name,

        address_1=address_1,

        phone=phone,

        website=website,

        notes=notes

    )


    db.add(vendor)

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vendors-ui",
        status_code=303
    )

# --------------------------------------------------
# Archived Vehicles
# --------------------------------------------------

@router.get(
    "/vehicles-archived",
    response_class=HTMLResponse
)
def archived_vehicles(
    request: Request
):

    db = SessionLocal()

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == True
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicles_archived.html",
        context={
            "request": request,
            "vehicles": vehicles
        }
    )
# --------------------------------------------------
# Vehicle Maintenance Add Page
# --------------------------------------------------

@router.get(
    "/vehicle/{vehicle_id}/maintenance-add",
    response_class=HTMLResponse
)
def vehicle_maintenance_add_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vendors = db.query(
        Vendor
    ).all()

    service_types = db.query(
        ServiceType
    ).filter(
        ServiceType.archived == False
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_add_vehicle.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "vehicle_id": vehicle.id,
            "vendors": vendors,
            "service_types": service_types
        }
    )
# --------------------------------------------------
# Vehicle Maintenance Add Submit
# --------------------------------------------------

@router.post(
    "/vehicle/{vehicle_id}/maintenance-add"
)
def vehicle_maintenance_add_submit(

    vehicle_id: int,

    vendor_id: int = Form(...),

    visit_date: str = Form(...),

    mileage: int = Form(...),

    invoice_number: str = Form(""),

    total_cost: float = Form(0),

    primary_reason: str = Form(...),

    other_service: str = Form(""),

    document_file: UploadFile | None = File(None)

):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    visit = MaintenanceVisit(

        vehicle_id=vehicle_id,

        vendor=vendor.name,

        visit_date=visit_date,

        mileage=mileage,

        invoice_number=invoice_number,

        total_cost=total_cost

    )

    db.add(visit)

    db.commit()

    db.refresh(visit)

    if primary_reason == "Other":

        primary_reason = other_service
    service = ServiceRecord(

        vehicle_id=vehicle_id,

        maintenance_visit_id=visit.id,

        primary_reason=primary_reason,

        service_status="COMPLETED"
    )

    db.add(service)

    db.commit()
    print("MAINTENANCE VISIT CREATED")
    print("document_file =", document_file)
    print("filename =", document_file.filename if document_file else None)

    if document_file and document_file.filename:

        print("UPLOAD BLOCK ENTERED")

        vehicle = db.query(
            Vehicle
        ).filter(
            Vehicle.id == vehicle_id
        ).first()

        print("VEHICLE FOUND")

        maintenance_folder = get_maintenance_folder(
            vehicle,
            visit,
            primary_reason
        )

        print("FOLDER =", maintenance_folder)

        original_extension = (
            document_file.filename
            .split(".")[-1]
        )

        destination = os.path.join(
            maintenance_folder,
            f"Invoice.{original_extension}"
        )

        with open(
            destination,
            "wb"
        ) as buffer:

            buffer.write(
                document_file.file.read()
            )
    db.close()

    return RedirectResponse(
        url=f"/vehicle/{vehicle_id}",
        status_code=303
    )

# --------------------------------------------------
# Vehicle Maintenance History
# --------------------------------------------------

@router.get(
    "/vehicle/{vehicle_id}/maintenance",
    response_class=HTMLResponse
)
def vehicle_maintenance_history(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    visits = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.vehicle_id == vehicle_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_maintenance.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "visits": visits
        }
    )
# --------------------------------------------------
# Vehicle Documents
# --------------------------------------------------

@router.get(
    "/vehicle/{vehicle_id}/documents",
    response_class=HTMLResponse
)
def vehicle_documents(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    documents = db.query(
        Document
    ).filter(
        Document.vehicle_id == vehicle_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_documents.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "documents": documents
        }
    )
# --------------------------------------------------
# Add Document Page
# --------------------------------------------------

@router.get(
    "/vehicle/{vehicle_id}/document-add",
    response_class=HTMLResponse
)
def document_add_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="document_add.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
