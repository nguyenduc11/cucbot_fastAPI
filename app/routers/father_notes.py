from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Literal
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_flask_web_database
from ..models import (
    FatherNote,
    FatherNoteCreate,
    FatherNoteUpdate,
    FatherNoteResponse,
    FatherNoteInDB,
    father_note_helper
)

router = APIRouter(prefix="/father_notes", tags=["father_notes"])

@router.get("/", response_model=FatherNoteResponse)
async def get_father_notes(
    sort_by: str = Query("datePosted", description="Field to sort by"),
    order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    filter: Optional[Literal["week", "month"]] = Query(None, description="Date filter")
):
    """Get all father notes with optional filtering and sorting"""
    try:
        db = get_flask_web_database()
        
        query = {}
        
        if filter == "week":
            one_week_ago = datetime.now() - timedelta(days=7)
            query["datePosted"] = {"$gte": one_week_ago}
        elif filter == "month":
            one_month_ago = datetime.now() - timedelta(days=30)
            query["datePosted"] = {"$gte": one_month_ago}
        
        sort_order = 1 if order == "asc" else -1
        
        cursor = db.father_notes.find(query).sort(sort_by, sort_order).limit(10)
        notes = await cursor.to_list(length=10)
        converted_notes = [father_note_helper(note) for note in notes]
        
        return FatherNoteResponse(
            success=True,
            notes=converted_notes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch notes: {str(e)}"
        )

@router.post("/", response_model=FatherNoteResponse)
async def create_father_note(note_data: FatherNoteCreate):
    """Create a new father note"""
    try:
        db = get_flask_web_database()
        
        new_note = {
            "title": note_data.title.strip(),
            "description": note_data.description.strip(),
            "datePosted": datetime.now(),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await db.father_notes.insert_one(new_note)
        created_note = await db.father_notes.find_one({"_id": result.inserted_id})
        
        return FatherNoteResponse(
            success=True,
            note=father_note_helper(created_note)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create note: {str(e)}"
        )

@router.get("/recent", response_model=FatherNoteResponse)
async def get_recent_father_note():
    """Get the most recent father note"""
    try:
        db = get_flask_web_database()
        
        recent_note = await db.father_notes.find_one(
            {},
            sort=[("datePosted", -1)]
        )
        
        return FatherNoteResponse(
            success=True,
            note=father_note_helper(recent_note) if recent_note else None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent note: {str(e)}"
        )

@router.get("/{note_id}", response_model=FatherNoteResponse)
async def get_father_note(note_id: str):
    """Get a specific father note by ID"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid note ID"
            )
        
        db = get_flask_web_database()
        note = await db.father_notes.find_one({"_id": ObjectId(note_id)})
        
        if not note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        
        return FatherNoteResponse(
            success=True,
            note=father_note_helper(note)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch note: {str(e)}"
        )

@router.put("/{note_id}", response_model=FatherNoteResponse)
async def update_father_note(note_id: str, note_data: FatherNoteUpdate):
    """Update a father note"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid note ID"
            )
        
        db = get_flask_web_database()
        update_data = {
            "title": note_data.title.strip(),
            "description": note_data.description.strip(),
            "updatedAt": datetime.now()
        }
        
        result = await db.father_notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        
        updated_note = await db.father_notes.find_one({"_id": ObjectId(note_id)})
        
        return FatherNoteResponse(
            success=True,
            note=father_note_helper(updated_note)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update note: {str(e)}"
        )

@router.delete("/{note_id}", response_model=FatherNoteResponse)
async def delete_father_note(note_id: str):
    """Delete a father note"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid note ID"
            )
        
        db = get_flask_web_database()
        result = await db.father_notes.delete_one({"_id": ObjectId(note_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        
        return FatherNoteResponse(
            success=True,
            message="Note deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete note: {str(e)}"
        )
