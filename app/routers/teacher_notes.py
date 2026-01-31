from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Literal
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_flask_web_database
from ..models import (
    TeacherNote, 
    TeacherNoteCreate, 
    TeacherNoteUpdate, 
    TeacherNoteResponse,
    TeacherNoteInDB,
    teacher_note_helper
)

router = APIRouter(prefix="/teacher_notes", tags=["teacher_notes"])

@router.get("/", response_model=TeacherNoteResponse)
async def get_teacher_notes(
    sort_by: str = Query("datePosted", description="Field to sort by"),
    order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    filter: Optional[Literal["week", "month"]] = Query(None, description="Date filter")
):
    """Get all teacher notes with optional filtering and sorting"""
    try:
        db = get_flask_web_database()
        
        # Build query filter
        query = {}
        
        # Apply date filtering
        if filter == "week":
            one_week_ago = datetime.now() - timedelta(days=7)
            query["datePosted"] = {"$gte": one_week_ago}
        elif filter == "month":
            one_month_ago = datetime.now() - timedelta(days=30)
            query["datePosted"] = {"$gte": one_month_ago}
        
        # Convert sort order
        sort_order = 1 if order == "asc" else -1
        
        # Execute query - limit to 10 most recent notes
        cursor = db.teacher_notes.find(query).sort(sort_by, sort_order).limit(10)
        notes = await cursor.to_list(length=10)
        
        # Convert documents using helper function
        converted_notes = [teacher_note_helper(note) for note in notes]
        
        return TeacherNoteResponse(
            success=True,
            notes=converted_notes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch notes: {str(e)}"
        )

@router.post("/", response_model=TeacherNoteResponse)
async def create_teacher_note(note_data: TeacherNoteCreate):
    """Create a new teacher note"""
    try:
        db = get_flask_web_database()
        
        # Create new note document (matching your MongoDB structure)
        new_note = {
            "title": note_data.title.strip(),
            "description": note_data.description.strip(),  # HTML content preserved
            "datePosted": datetime.now(),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Insert into database
        result = await db.teacher_notes.insert_one(new_note)
        
        # Get the created note and convert using helper
        created_note = await db.teacher_notes.find_one({"_id": result.inserted_id})
        
        return TeacherNoteResponse(
            success=True,
            note=teacher_note_helper(created_note)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create note: {str(e)}"
        )

@router.get("/recent", response_model=TeacherNoteResponse)
async def get_recent_teacher_note():
    """Get the most recent teacher note"""
    try:
        db = get_flask_web_database()
        
        # Debug: Check if collection exists and has documents
        collection_names = await db.list_collection_names()
        print(f"Available collections: {collection_names}")
        
        # Check document count
        doc_count = await db.teacher_notes.count_documents({})
        print(f"Total documents in teacher_notes: {doc_count}")
        
        # Find the most recent note with debugging
        recent_note = await db.teacher_notes.find_one(
            {},
            sort=[("datePosted", -1)]
        )
        
        print(f"Recent note found: {recent_note is not None}")
        if recent_note:
            print(f"Recent note ID: {recent_note.get('_id')}")
            print(f"Recent note title: {recent_note.get('title')}")
        
        return TeacherNoteResponse(
            success=True,
            note=teacher_note_helper(recent_note) if recent_note else None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Error in get_recent_teacher_note: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent note: {str(e)}"
        )

@router.get("/{note_id}", response_model=TeacherNoteResponse)
async def get_teacher_note(note_id: str):
    """Get a specific teacher note by ID"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid note ID"
            )
        
        db = get_flask_web_database()
        
        # Find the note
        note = await db.teacher_notes.find_one({"_id": ObjectId(note_id)})
        
        if not note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        
        return TeacherNoteResponse(
            success=True,
            note=teacher_note_helper(note)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch note: {str(e)}"
        )

@router.put("/{note_id}", response_model=TeacherNoteResponse)
async def update_teacher_note(note_id: str, note_data: TeacherNoteUpdate):
    """Update a teacher note"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid note ID"
            )
        
        db = get_flask_web_database()
        
        # Prepare update data (matching your MongoDB structure)
        update_data = {
            "title": note_data.title.strip(),
            "description": note_data.description.strip(),  # HTML content preserved
            "updatedAt": datetime.now()
        }
        
        # Update the note
        result = await db.teacher_notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        
        # Get the updated note and convert using helper
        updated_note = await db.teacher_notes.find_one({"_id": ObjectId(note_id)})
        
        return TeacherNoteResponse(
            success=True,
            note=teacher_note_helper(updated_note)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update note: {str(e)}"
        )

@router.delete("/{note_id}", response_model=TeacherNoteResponse)
async def delete_teacher_note(note_id: str):
    """Delete a teacher note"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid note ID"
            )
        
        db = get_flask_web_database()
        
        # Delete the note
        result = await db.teacher_notes.delete_one({"_id": ObjectId(note_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        
        return TeacherNoteResponse(
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
