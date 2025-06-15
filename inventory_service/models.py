from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    location = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    inventory_items = relationship("Inventory", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse(id='{self.id}', name='{self.name}')>"


class Inventory(Base):
    __tablename__ = "inventory"
    
    product_id = Column(String, primary_key=True, nullable=False)
    warehouse_id = Column(String, ForeignKey("warehouses.id"), primary_key=True, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    
    def __repr__(self):
        return f"<Inventory(product_id='{self.product_id}', warehouse_id='{self.warehouse_id}', stock={self.stock})>"