import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry
from database import database, engine
from models import Base
from schema import Query, Mutation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events"""
    # Startup
    await database.connect()
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database connected and tables created")
    
    yield
    
    # Shutdown
    await database.disconnect()
    print("Database disconnected")


# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Create FastAPI app
app = FastAPI(
    title="Inventory Service",
    description="GraphQL API for inventory and warehouse management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")

# Add REST endpoints for backward compatibility
from rest_adapter import router as rest_router
app.include_router(rest_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Inventory Services API",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "/graphql (in browser)",
        "rest_endpoints": "Available at /warehouses, /inventory/product/{id}, /inventory/warehouse/{id}"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5003))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("NODE_ENV") != "production" else False
    )