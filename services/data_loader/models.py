from pydantic import BaseModel, Field
from typing import Optional

class Soldier(BaseModel):
    """Model representing an enemy soldier record"""
    id: int = Field(..., description="Unique numeric ID")
    first_name: str = Field(..., description="Soldier's first name")
    last_name: str = Field(..., description="Soldier's last name")
    phone_number: str = Field(..., description="Soldier's phone number")
    rank: str = Field(..., description="Soldier's military rank")

class SoldierCreate(BaseModel):
    """Model for creating a new soldier (without ID)"""
    first_name: str = Field(..., description="Soldier's first name")
    last_name: str = Field(..., description="Soldier's last name")
    phone_number: str = Field(..., description="Soldier's phone number")
    rank: str = Field(..., description="Soldier's military rank")
    
class SoldierUpdate(BaseModel):
    """Model for updating a soldier"""
    first_name: Optional[str] = Field(None, description="Soldier's first name")
    last_name: Optional[str] = Field(None, description="Soldier's last name")
    phone_number: Optional[str] = Field(None, description="Soldier's phone number")
    rank: Optional[str] = Field(None, description="Soldier's military rank")
    
class ResponseMessage(BaseModel):
    """Standard response message for operations"""
    message: str
    success: bool
    data: Optional[dict] = None