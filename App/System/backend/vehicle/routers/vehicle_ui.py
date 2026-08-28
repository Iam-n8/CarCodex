# Vehicle UI Routes
import os
import requests

from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse
)

from shared.template_loader import (
    templates
)

from database import SessionLocal

from models import (
    Vehicle,
    MaintenanceVisit,
    MaintenanceSchedule,
    Document,
    Vendor,
    ServiceRecord,
    ServiceGroup,
    ServiceItem
)

from helpers.storage import (
    create_vehicle_folders,
    create_vehicle_info_file,
    get_maintenance_folder,
    save_vin_decode_files
    )
from helpers.service_catalog_loader import (
    load_available_domains
)

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP
)

router = APIRouter()

# --------------------------------------------------
# Currency Conversion
# --------------------------------------------------

def dollars_to_cents(
    value: str
):
    """
    Convert a dollar amount submitted by a form
    into integer cents.

    Examples:

    "38500.00" -> 3850000
    "" -> None
    """

    if value is None:

        return None

    cleaned_value = value.strip()

    if not cleaned_value:

        return None

    try:

        dollar_amount = Decimal(
            cleaned_value
        )

    except InvalidOperation:

        return None

    if dollar_amount < 0:

        return None

    cent_amount = (
        dollar_amount * 100
    ).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    return int(
        cent_amount
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

    for vehicle in vehicles:

        highest_mileage = vehicle.current_mileage

        visits = db.query(
            MaintenanceVisit
        ).filter(
            MaintenanceVisit.vehicle_id == vehicle.id
        ).all()

        for visit in visits:

            if (
                visit.mileage is not None
                and visit.mileage > highest_mileage
            ):
                highest_mileage = visit.mileage

        vehicle.display_mileage = highest_mileage

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

    # Display highest mileage found
    display_mileage = vehicle.current_mileage

    visit_mileages = [
        visit.mileage
        for visit in visits
        if visit.mileage is not None
    ]

    if visit_mileages:
        display_mileage = max(
            display_mileage,
            max(visit_mileages)
        )

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

            "vendor_count": 0,

            "display_mileage": display_mileage
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

    nickname: str = Form(""),

    vin: str = Form(""),

    year: int = Form(...),

    make: str = Form(""),

    model: str = Form(""),

    trim: str = Form(""),

    current_mileage: int = Form(...),

    date_acquired: str = Form(""),

    mileage_at_acquisition: int | None = Form(None),

    vehicle_condition: str = Form(""),

    purchase_price: str = Form(""),

    sold_price: str = Form("")

):



    if not nickname.strip():
        nickname = "Nickname Unknown"

    if not make.strip():
        make = "Make Unknown"

    if not model.strip():
        model = "Model Unknown"

    if not trim.strip():
        trim = "Trim Unknown"

    if not vin.strip():
        vin = "VIN Unknown"

    print("VEHICLE ADD SUBMIT REACHED")

    db = SessionLocal()

    purchase_price_cents = dollars_to_cents(
        purchase_price
    )

    sold_price_cents = dollars_to_cents(
        sold_price
    )

    vehicle = Vehicle(

        nickname=nickname,

        vin=vin,

        year=year,

        make=make,

        model=model,

        trim=trim,

        current_mileage=current_mileage,

        date_acquired=(
            date_acquired.strip()
            if date_acquired.strip()
            else None
        ),

        mileage_at_acquisition=mileage_at_acquisition,

        vehicle_condition=(
            vehicle_condition.strip()
            if vehicle_condition.strip()
            else None
        ),

        purchase_price_cents=purchase_price_cents,

        sold_price_cents=sold_price_cents,

        archived=False

    )

    db.add(vehicle)

    db.commit()

    db.refresh(vehicle)

    create_vehicle_folders(
        vehicle
    )

    if (
        vin
        and vin != "VIN Unknown"
    ):

        try:

            url = (
                "https://vpic.nhtsa.dot.gov/api/"
                f"vehicles/DecodeVinValues/{vin}"
                "?format=json"
            )

            response = requests.get(
                url,
                timeout=10
            )

            response.raise_for_status()

            decode_data = response.json()

            save_vin_decode_files(
                vehicle,
                decode_data
            )

        except Exception as error:

            print(
                "VIN decode export failed:",
                error
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

    nickname: str = Form(""),

    vin: str = Form(""),

    year: int = Form(...),

    make: str = Form(""),

    model: str = Form(""),

    trim: str = Form(""),

    current_mileage: int = Form(...),

    date_acquired: str = Form(""),

    mileage_at_acquisition: int | None = Form(None),

    vehicle_condition: str = Form(""),

    purchase_price: str = Form(""),

    sold_price: str = Form("")

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
    vehicle.date_acquired = (
        date_acquired.strip()
        if date_acquired.strip()
        else None
    )

    vehicle.mileage_at_acquisition = (
        mileage_at_acquisition
    )

    vehicle.vehicle_condition = (
        vehicle_condition.strip()
        if vehicle_condition.strip()
        else None
    )

    vehicle.purchase_price_cents = dollars_to_cents(
        purchase_price
  
    )

    vehicle.sold_price_cents = dollars_to_cents(
        sold_price

    )


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
    ).filter(
        Vendor.archived == False,
        (
            (Vendor.domain == "Vehicle")
            | (Vendor.domain == None)
        )
    ).order_by(
        Vendor.is_preferred.desc(),
        Vendor.name
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
    request: Request,
    domain: str = ""
):


    available_domains = load_available_domains()

    return templates.TemplateResponse(
        request=request,
        name="vendor_add.html",
        context={
            "request": request,
            "available_domains": available_domains,
            "domain": domain
        }
    )

# --------------------------------------------------
# Add Vendor Submit
# --------------------------------------------------

@router.post(
    "/vendor-add"
)
def vendor_add_submit(

    name: str = Form(...),

    vendor_type: str = Form(""),

    domain: str = Form(""),

    rating: int | None = Form(None),

    address_1: str = Form(""),

    address_2: str = Form(""),

    city: str = Form(""),

    state: str = Form(""),

    zip_code: str = Form(""),

    primary_contact: str = Form(""),

    phone: str = Form(""),

    email: str = Form(""),

    website: str = Form(""),

    is_preferred: str = Form(""),

    notes: str = Form("")

):

    # ----------------------------------------------
    # Clean and Validate Values
    # ----------------------------------------------

    name = name.strip()

    if not name:

        name = "Vendor Name Unknown"

    vendor_type = vendor_type.strip()

    domain = domain.strip()

    address_1 = address_1.strip()

    address_2 = address_2.strip()

    city = city.strip()

    state = state.strip().upper()

    zip_code = zip_code.strip()

    primary_contact = primary_contact.strip()

    phone = phone.strip()

    email = email.strip()

    website = website.strip()

    notes = notes.strip()

    if (
        rating is not None
        and rating not in [
            1,
            2,
            3,
            4,
            5
        ]
    ):

        rating = None

    preferred_value = (
        is_preferred == "on"
    )

    # ----------------------------------------------
    # Create Vendor
    # ----------------------------------------------

    db = SessionLocal()

    vendor = Vendor(

        name=name,

        vendor_type=(
            vendor_type
            if vendor_type
            else None
        ),

        domain=(
            domain
            if domain
            else None
        ),

        rating=rating,

        address_1=(
            address_1
            if address_1
            else None
        ),

        address_2=(
            address_2
            if address_2
            else None
        ),

        city=(
            city
            if city
            else None
        ),

        state=(
            state
            if state
            else None
        ),

        zip_code=(
            zip_code
            if zip_code
            else None
        ),

        primary_contact=(
            primary_contact
            if primary_contact
            else None
        ),

        phone=(
            phone
            if phone
            else None
        ),

        email=(
            email
            if email
            else None
        ),

        website=(
            website
            if website
            else None
        ),

        is_preferred=preferred_value,

        notes=(
            notes
            if notes
            else None
        ),

        archived=False

    )

    db.add(
        vendor
    )

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
    vehicle_id: int,
    schedule_id: int | None = None
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

    selected_schedule = None

    preselected_service = ""

    if schedule_id is not None:

        selected_schedule = db.query(
            MaintenanceSchedule
        ).filter(
            MaintenanceSchedule.id == schedule_id,
            MaintenanceSchedule.vehicle_id == vehicle_id
        ).first()

        if selected_schedule:

            preselected_service = (
                selected_schedule.service_type_match
                or selected_schedule.item_name
                or ""
            )

    # ----------------------------------------------
    # Optional MaintSch Preselection
    # ----------------------------------------------

    selected_schedule = None

    preselected_service = ""

    if schedule_id is not None:

        selected_schedule = db.query(
            MaintenanceSchedule
        ).filter(
            MaintenanceSchedule.id == schedule_id,
            MaintenanceSchedule.vehicle_id == vehicle_id
        ).first()

        if selected_schedule:

            preselected_service = (
                selected_schedule.service_type_match
                or selected_schedule.item_name
                or ""
            )

    # ----------------------------------------------
    # Vendors
    # ----------------------------------------------

    vendors = db.query(
        Vendor
    ).filter(
        Vendor.archived == False,
        (
            (Vendor.domain == "Vehicle")
            | (Vendor.domain == None)
        )
    ).order_by(
        Vendor.is_preferred.desc(),
        Vendor.name
    ).all()

    # ----------------------------------------------
    # Service Catalog
    # ----------------------------------------------

    service_groups = db.query(
        ServiceGroup
    ).filter(
        ServiceGroup.inactive == False
    ).order_by(
        ServiceGroup.display_order
    ).all()

    service_catalog = []

    for group in service_groups:

        items = db.query(
            ServiceItem
        ).filter(
            ServiceItem.group_id == group.id,
            ServiceItem.inactive == False
        ).order_by(
            ServiceItem.display_order
        ).all()

        service_catalog.append(
            {
                "group": group,
                "items": items
            }
        )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_add_vehicle.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "vehicle_id": vehicle.id,
            "vendors": vendors,
            "service_catalog": service_catalog,
            "selected_schedule": selected_schedule,
            "preselected_service": preselected_service
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

    additional_services: list[str] = Form([]),

    custom_services: str = Form(""),

    service_notes: str = Form(""),

    schedule_id: int | None = Form(None),

    document_file: UploadFile | None = File(None)


):
    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    if not vendor:

        db.close()

        return RedirectResponse(
            url=f"/vehicle/{vehicle_id}/maintenance-add",
            status_code=303
        )


    visit = MaintenanceVisit(

    vehicle_id=vehicle_id,

    vendor_id=vendor.id,

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
    all_additional_services = additional_services.copy()

    if custom_services.strip():

        all_additional_services.append(
            custom_services.strip()
        )

    service = ServiceRecord(

        vehicle_id=vehicle_id,

        maintenance_visit_id=visit.id,

        primary_reason=primary_reason,

        additional_services="\n".join(
            all_additional_services
        ),

        notes=service_notes,

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


        document = Document(

            vehicle_id=vehicle_id,

            maintenance_visit_id=visit.id,

            document_type="Receipt",

            file_name=os.path.basename(
                destination
            ),

            file_path=destination,

            upload_date=visit_date,

            notes=primary_reason
        )

        db.add(document)

        db.commit()


            
    db.close()

    if schedule_id is not None:

        return RedirectResponse(
            url=f"/maintenance-due-ui/{vehicle_id}",
            status_code=303
        )

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
# --------------------------------------------------
# Maintenance Document Add Page
# --------------------------------------------------

@router.get(
    "/maintenance/{visit_id}/document-add",
    response_class=HTMLResponse
)
def maintenance_document_add_page(
    request: Request,
    visit_id: int
):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == visit.vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_document_add.html",
        context={
            "request": request,
            "visit": visit,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Maintenance Document Add Page
# --------------------------------------------------

@router.get(
    "/maintenance/{visit_id}/document-add",
    response_class=HTMLResponse
)
def maintenance_document_add_page(
    request: Request,
    visit_id: int
):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == visit.vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_document_add.html",
        context={
            "request": request,
            "visit": visit,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Maintenance Document Add Submit
# --------------------------------------------------

@router.post(
    "/maintenance/{visit_id}/document-add"
)
def maintenance_document_add_submit(

    visit_id: int,

    document_type: str = Form(...),

    notes: str = Form(""),

    document_file: UploadFile = File(...)

):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == visit.vehicle_id
    ).first()

    service = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.maintenance_visit_id == visit_id
    ).first()

    primary_reason = "Other"

    if service:
        primary_reason = (
            service.primary_reason
        )

    maintenance_folder = get_maintenance_folder(
        vehicle,
        visit,
        primary_reason
    )

    extension = (
        document_file.filename
        .split(".")[-1]
    )

    filename = (
        f"{document_type}."
        f"{extension}"
    )

    destination = os.path.join(
        maintenance_folder,
        filename
    )

    with open(
        destination,
        "wb"
    ) as buffer:

        buffer.write(
            document_file.file.read()
        )

    document = Document(

        vehicle_id=vehicle.id,

        maintenance_visit_id=visit.id,

        document_type=document_type,

        file_name=filename,

        file_path=destination,

        upload_date=visit.visit_date,

        notes=notes
    )

    db.add(document)

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintenance-visit/{visit_id}",
        status_code=303
    )
# --------------------------------------------------
# VIN Decode
# --------------------------------------------------

@router.get(
    "/vin-decode"
)
def vin_decode(
    vin: str
):

    url = (
        "https://vpic.nhtsa.dot.gov/api/"
        f"vehicles/DecodeVinValues/{vin}"
        "?format=json"
    )

    response = requests.get(
        url,
        timeout=10
    )

    data = response.json()

    result = data["Results"][0]

    return JSONResponse(
        content=result
    )