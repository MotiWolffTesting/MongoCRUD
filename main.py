from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from services.data_loader.dal import SoldierDal
from services.data_loader.models import SoldierCreate, SoldierUpdate, ResponseMessage
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DAL
# Get MongoDB connection string from .env or default
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
soldier_dal = SoldierDal(mongodb_uri)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app):
    "Manage app startup and shutdown for DB connection."
    try:
        connected = soldier_dal.connect()
        if not connected:
            logger.error("Failed to connect to MongoDB.")
        else:
            logger.info("Successfully connected to MongoDB!")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    yield
    soldier_dal.close()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Enemy Soldiers CRUD API",
    description="REST API for managing enemy soldiers database",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/soldiersdb/", response_model=ResponseMessage)
async def get_all_soldiers():
    "Get all soldiers from the database"
    try:
        result = soldier_dal.get_all_soldiers()
        if result.success:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        logger.error(f"Error in get_all_soldiers endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/soldiersdb/", response_model=ResponseMessage)
async def create_soldier(soldier_data: SoldierCreate):
    "Create a new soldier record"
    try:
        result = soldier_dal.create_soldier(soldier_data)
        if result.success:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except Exception as e:
        logger.error(f"Error in create_soldier endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/soldiersdb/{soldier_id}", response_model=ResponseMessage)
async def update_soldier(soldier_id: int, update_data: SoldierUpdate):
    "Update a soldier record by ID"
    try:
        result = soldier_dal.update_soldier(soldier_id, update_data)
        if result.success:
            return result
        else:
            if "not found" in result.message.lower():
                raise HTTPException(status_code=404, detail=result.message)
            else:
                raise HTTPException(status_code=400, detail=result.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_soldier endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.delete("/soldiersdb/{soldier_id}", response_model=ResponseMessage)
async def delete_soldier(soldier_id: int):
    "Delete a soldier record by ID"
    try:
        result = soldier_dal.delete_soldier(soldier_id)
        if result.success:
            return result
        else:
            if "not found" in result.message.lower():
                raise HTTPException(status_code=404, detail=result.message)
            else:
                raise HTTPException(status_code=400, detail=result.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_soldier endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/soldiersdb/{soldier_id}", response_model=ResponseMessage)
async def get_soldier_by_id(soldier_id: int):
    "Get a specific soldier by ID"
    try:
        result = soldier_dal.get_soldier_by_id(soldier_id)
        if result.success:
            return result
        else:
            if "not found" in result.message.lower():
                raise HTTPException(status_code=404, detail=result.message)
            else:
                raise HTTPException(status_code=400, detail=result.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_soldier_by_id endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
