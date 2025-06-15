from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select
from database import database
from models import Warehouse as WarehouseModel, Inventory as InventoryModel
from datetime import datetime

router = APIRouter()

# Pydantic models for REST API
class WarehouseResponse(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class InventoryResponse(BaseModel):
    product_id: str
    warehouse_id: str
    stock: int
    updated_at: datetime
    warehouse: Optional[WarehouseResponse] = None

class UpdateStockRequest(BaseModel):
    product_id: str
    warehouse_id: str
    quantity_change: int

class CreateWarehouseRequest(BaseModel):
    id: str
    name: str
    location: Optional[str] = None


@router.get("/warehouses", response_model=List[WarehouseResponse])
async def get_all_warehouses():
    """Get all warehouses"""
    query = select(WarehouseModel)
    result = await database.fetch_all(query)
    return [
        WarehouseResponse(
            id=row.id,
            name=row.name,
            location=row.location,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        for row in result
    ]


@router.get("/inventory/product/{product_id}", response_model=List[InventoryResponse])
async def get_inventory_by_product(product_id: str):
    """Get inventory by product ID"""
    query = (
        select(InventoryModel, WarehouseModel)
        .join(WarehouseModel, InventoryModel.warehouse_id == WarehouseModel.id)
        .where(InventoryModel.product_id == product_id)
    )
    result = await database.fetch_all(query)
    
    return [
        InventoryResponse(
            product_id=row.product_id,
            warehouse_id=row.warehouse_id,
            stock=row.stock,
            updated_at=row.updated_at,
            warehouse=WarehouseResponse(
                id=row.id,
                name=row.name,
                location=row.location,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
        )
        for row in result
    ]


@router.get("/inventory/warehouse/{warehouse_id}", response_model=List[InventoryResponse])
async def get_inventory_by_warehouse(warehouse_id: str):
    """Get inventory by warehouse ID"""
    query = (
        select(InventoryModel, WarehouseModel)
        .join(WarehouseModel, InventoryModel.warehouse_id == WarehouseModel.id)
        .where(InventoryModel.warehouse_id == warehouse_id)
    )
    result = await database.fetch_all(query)
    
    return [
        InventoryResponse(
            product_id=row.product_id,
            warehouse_id=row.warehouse_id,
            stock=row.stock,
            updated_at=row.updated_at,
            warehouse=WarehouseResponse(
                id=row.id,
                name=row.name,
                location=row.location,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
        )
        for row in result
    ]


@router.post("/inventory/update", response_model=InventoryResponse)
async def update_stock(request: UpdateStockRequest):
    """Update inventory stock"""
    async with database.transaction():
        # Check if inventory record exists
        query = select(InventoryModel).where(
            InventoryModel.product_id == request.product_id,
            InventoryModel.warehouse_id == request.warehouse_id
        )
        existing = await database.fetch_one(query)
        
        if existing:
            # Calculate new stock
            new_stock = existing.stock + request.quantity_change
            
            # Check if stock would be negative
            if new_stock < 0:
                raise HTTPException(status_code=400, detail="Cannot reduce stock below zero")
            
            # Update existing record
            update_query = (
                InventoryModel.__table__.update()
                .where(
                    InventoryModel.product_id == request.product_id,
                    InventoryModel.warehouse_id == request.warehouse_id
                )
                .values(stock=new_stock, updated_at=datetime.now())
            )
            await database.execute(update_query)
        else:
            # Create new inventory record
            if request.quantity_change < 0:
                raise HTTPException(status_code=400, detail="Cannot create inventory with negative stock")
            
            insert_query = InventoryModel.__table__.insert().values(
                product_id=request.product_id,
                warehouse_id=request.warehouse_id,
                stock=request.quantity_change,
                updated_at=datetime.now()
            )
            await database.execute(insert_query)
        
        # Get updated record with warehouse info
        query_with_warehouse = (
            select(InventoryModel, WarehouseModel)
            .join(WarehouseModel, InventoryModel.warehouse_id == WarehouseModel.id)
            .where(
                InventoryModel.product_id == request.product_id,
                InventoryModel.warehouse_id == request.warehouse_id
            )
        )
        result = await database.fetch_one(query_with_warehouse)
        
        return InventoryResponse(
            product_id=result.product_id,
            warehouse_id=result.warehouse_id,
            stock=result.stock,
            updated_at=result.updated_at,
            warehouse=WarehouseResponse(
                id=result.id,
                name=result.name,
                location=result.location,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
        )


@router.post("/warehouses", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(request: CreateWarehouseRequest):
    """Create a new warehouse"""
    # Check if warehouse already exists
    query = select(WarehouseModel).where(WarehouseModel.id == request.id)
    existing = await database.fetch_one(query)
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Warehouse with ID {request.id} already exists")
    
    # Create new warehouse
    insert_query = WarehouseModel.__table__.insert().values(
        id=request.id,
        name=request.name,
        location=request.location,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await database.execute(insert_query)
    
    # Return created warehouse
    result = await database.fetch_one(query)
    return WarehouseResponse(
        id=result.id,
        name=result.name,
        location=result.location,
        created_at=result.created_at,
        updated_at=result.updated_at
    )