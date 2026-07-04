# import os
from routers import vehicles
from fastapi import FastAPI
from database import engine
from routers import mileage
from routers import events
from routers import documents
from routers import costs
from routers import snapshots
from models import Base



# --------------------------------------------------
# Routers
# --------------------------------------------------
from routers import services
app = FastAPI()
app.include_router(vehicles.router)
app.include_router(services.router) 
app.include_router(mileage.router)
app.include_router(events.router)
app.include_router(documents.router)
app.include_router(costs.router)
app.include_router(snapshots.router)


Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Helpers
# --------------------------------------------------



# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "app": "CarCodex",
        "version": "1.0.1",
        "status": "running"
    }


