from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from database.operations import (
    get_inventory,
    get_pending_scan_candidates,
    add_inventory_item
)

app = FastAPI(title="SmartStock API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class InventoryItemCreate(BaseModel):
    product_name: str
    barcode: Optional[str] = None
    category: Optional[str] = None
    quantity: float = 1
    unit: Optional[str] = None
    purchase_date: Optional[str] = None
    expiration_date: Optional[str] = None
    date_confirmed: int = 0


# --------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "SmartStock API is running!"}


@app.get("/inventory")
def read_inventory():
    items = get_inventory()

    return [dict(item) for item in items]


@app.get("/scan-candidates")
def read_scan_candidates():
    scans = get_pending_scan_candidates()

    return [dict(scan) for scan in scans]


@app.post("/inventory")
def create_inventory_item(item: InventoryItemCreate):

    item_id = add_inventory_item(
        product_name=item.product_name,
        barcode=item.barcode,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        purchase_date=item.purchase_date,
        expiration_date=item.expiration_date,
        date_confirmed=item.date_confirmed
    )

    return {
        "message": "Inventory item created successfully",
        "item_id": item_id
    }