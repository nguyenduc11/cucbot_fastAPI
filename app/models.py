from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any, Dict
from datetime import datetime
from bson import ObjectId

class TeacherNoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the teacher note")
    description: str = Field(..., min_length=1, description="Content of the teacher note")

class TeacherNoteCreate(TeacherNoteBase):
    """Model for creating a new teacher note"""
    pass

class TeacherNoteUpdate(TeacherNoteBase):
    """Model for updating an existing teacher note"""
    pass

class TeacherNote(BaseModel):
    """Model representing a teacher note from MongoDB"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: Optional[str] = Field(default=None, alias="_id", description="MongoDB ObjectId as string")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, description="HTML content allowed")
    datePosted: Optional[datetime] = Field(default=None, description="Date when note was posted")
    createdAt: Optional[datetime] = Field(default=None, description="Date when note was created")
    updatedAt: Optional[datetime] = Field(default=None, description="Date when note was last updated")
    
    @field_validator('id', mode='before')
    @classmethod
    def validate_object_id(cls, v: Any) -> Optional[str]:
        """Convert ObjectId to string for JSON serialization"""
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId string")
        raise ValueError("Invalid ObjectId type")

class TeacherNoteInDB(BaseModel):
    """Model for teacher note as stored in MongoDB (with ObjectId)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    description: str  # HTML content allowed
    datePosted: datetime = Field(default_factory=datetime.now)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

class TeacherNoteResponse(BaseModel):
    """Standardized API response model"""
    success: bool
    note: Optional[TeacherNote] = None
    notes: Optional[list[TeacherNote]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

# Helper functions for MongoDB operations
def teacher_note_helper(note: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to API response format"""
    return {
        "_id": str(note["_id"]) if "_id" in note else None,
        "title": note.get("title", ""),
        "description": note.get("description", ""),
        "datePosted": note.get("datePosted"),
        "createdAt": note.get("createdAt"),
        "updatedAt": note.get("updatedAt")
    }
