from typing import List, Optional
from datetime import datetime
import strawberry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from database import engine, database
from models import Warehouse as WarehouseModel, Inventory as InventoryModel


@strawberry.type
class Warehouse:
    id: str
    name: str
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def inventory(self) -> List["Inventory"]:
        """Get all inventory items for this warehouse"""
        query = select(InventoryModel).where(InventoryModel.warehouse_id == self.id)
        result = await database.fetch_all(query)
        return [
            Inventory(
                product_id=row.product_id,
                warehouse_id=row.warehouse_id,
                stock=row.stock,
                updated_at=row.updated_at
            )
            for row in result
        ]


@strawberry.type
class Inventory:
    product_id: str
    warehouse_id: str
    stock: int
    updated_at: datetime
    
    @strawberry.field
    async def warehouse(self) -> Optional[Warehouse]:
        """Get the warehouse for this inventory item"""
        query = select(WarehouseModel).where(WarehouseModel.id == self.warehouse_id)
        result = await database.fetch_one(query)
        if result:
            return Warehouse(
                id=result.id,
                name=result.name,
                location=result.location,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
        return None


@strawberry.input
class UpdateStockInput:
    product_id: str
    warehouse_id: str
    quantity_change: int  # Can be positive (addition) or negative (reduction)


@strawberry.input
class CreateWarehouseInput:
    id: str
    name: str
    location: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    async def get_inventory_by_product(self, product_id: str) -> List[Inventory]:
        """Get inventory status for a specific product across all warehouses"""
        query = select(InventoryModel).where(InventoryModel.product_id == product_id)
        result = await database.fetch_all(query)
        return [
            Inventory(
                product_id=row.product_id,
                warehouse_id=row.warehouse_id,
                stock=row.stock,
                updated_at=row.updated_at
            )
            for row in result
        ]
    
    @strawberry.field
    async def get_inventory_by_warehouse(self, warehouse_id: str) -> List[Inventory]:
        """Get inventory status for a specific warehouse"""
        query = select(InventoryModel).where(InventoryModel.warehouse_id == warehouse_id)
        result = await database.fetch_all(query)
        return [
            Inventory(
                product_id=row.product_id,
                warehouse_id=row.warehouse_id,
                stock=row.stock,
                updated_at=row.updated_at
            )
            for row in result
        ]
    
    @strawberry.field
    async def get_all_warehouses(self) -> List[Warehouse]:
        """Get all warehouses"""
        query = select(WarehouseModel)
        result = await database.fetch_all(query)
        return [
            Warehouse(
                id=row.id,
                name=row.name,
                location=row.location,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in result
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_stock(self, input: UpdateStockInput) -> Inventory:
        """Update stock for a product in a specific warehouse"""
        # Start a transaction
        async with database.transaction():
            # Check if inventory record exists
            query = select(InventoryModel).where(
                InventoryModel.product_id == input.product_id,
                InventoryModel.warehouse_id == input.warehouse_id
            )
            existing = await database.fetch_one(query)
            
            if existing:
                # Calculate new stock
                new_stock = existing.stock + input.quantity_change
                
                # Check if stock would be negative
                if new_stock < 0:
                    raise Exception("Cannot reduce stock below zero")
                
                # Update existing record
                update_query = (
                    InventoryModel.__table__.update()
                    .where(
                        InventoryModel.product_id == input.product_id,
                        InventoryModel.warehouse_id == input.warehouse_id
                    )
                    .values(stock=new_stock, updated_at=datetime.now())
                )
                await database.execute(update_query)
                
                # Return updated record
                result = await database.fetch_one(query)
                return Inventory(
                    product_id=result.product_id,
                    warehouse_id=result.warehouse_id,
                    stock=result.stock,
                    updated_at=result.updated_at
                )
            else:
                # Create new inventory record
                if input.quantity_change < 0:
                    raise Exception("Cannot create inventory with negative stock")
                
                insert_query = InventoryModel.__table__.insert().values(
                    product_id=input.product_id,
                    warehouse_id=input.warehouse_id,
                    stock=input.quantity_change,
                    updated_at=datetime.now()
                )
                await database.execute(insert_query)
                
                # Return new record
                result = await database.fetch_one(query)
                return Inventory(
                    product_id=result.product_id,
                    warehouse_id=result.warehouse_id,
                    stock=result.stock,
                    updated_at=result.updated_at
                )
    
    @strawberry.mutation
    async def create_warehouse(self, input: CreateWarehouseInput) -> Warehouse:
        """Create a new warehouse"""
        # Check if warehouse already exists
        query = select(WarehouseModel).where(WarehouseModel.id == input.id)
        existing = await database.fetch_one(query)
        
        if existing:
            raise Exception(f"Warehouse with ID {input.id} already exists")
        
        # Create new warehouse
        insert_query = WarehouseModel.__table__.insert().values(
            id=input.id,
            name=input.name,
            location=input.location,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await database.execute(insert_query)
        
        # Return created warehouse
        result = await database.fetch_one(query)
        return Warehouse(
            id=result.id,
            name=result.name,
            location=result.location,
            created_at=result.created_at,
            updated_at=result.updated_at
        )