 # cucbot_fastAPI
 
 FastAPI backend for the cucbot project.
 
 This project uses **uv** for Python package and virtual environment management and **FastAPI + Uvicorn** for the web API.
 
 ## Prerequisites
 
 - Python **3.12+**
 - `pip` available in your shell
 
 > You do **not** need to install dependencies with `pip install -r requirements.txt` manually—`uv` will manage everything from `pyproject.toml` and `uv.lock`.
 
 ## 1. Install `uv` (one time per machine)
 
 In a terminal (PowerShell on Windows is fine):
 
 ```powershell
 pip install uv
 ```
 
 After this, the `uv` command should be available in your PATH.
 
 ## 2. Create the virtual environment
 
 From the project root:
 
 ```powershell
 cd d:\DUC\FastAPI\cucbot_fastAPI  # or the path where you cloned this repo
 
 uv venv
 ```
 
 This will:
 
 - Download a compatible Python (if needed)
 - Create a local virtual environment at `.venv/`
 
 ## 3. Activate the virtual environment
 
 Still in the project root, activate the venv:
 
 ```powershell
 .\.venv\Scripts\Activate.ps1
 ```
 
 Your prompt should now be prefixed with something like `(.venv)`.
 
 On other shells/platforms, activation commands are different, for example:
 
 - **cmd.exe (Windows):** `\.venv\Scripts\activate.bat`
 - **bash/zsh (Linux/macOS):** `source .venv/bin/activate`
 
 ## 4. Install dependencies with `uv sync`
 
 With the virtual environment active:
 
 ```powershell
 uv sync
 ```
 
 This will:
 
 - Read dependencies from `pyproject.toml`
 - Use `uv.lock` to install the exact pinned versions
 
 You do not need to call `pip install` manually.
 
 ## 5. Run the FastAPI development server
 
 With the venv still active and from the project root, you have two main options:
 
 ### Option A (recommended): run Uvicorn via `uv`
 
 ```powershell
 uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
 ```
 
 ### Option B: use the FastAPI CLI
 
 ```powershell
 uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
 ```
 
 After either command starts successfully, the backend will be available at:
 
 ```text
 http://localhost:8000/
 ```
 
 The basic health check endpoint is:
 
 - `GET /` → returns `{ "Message": "Hello World" }`
 
 ## 6. Stopping the server
 
 Press `Ctrl + C` in the terminal where the server is running.
 
To leave the virtual environment, run:
 
```powershell
deactivate
```
 
## Working with Pydantic and Motor

This project uses **Pydantic v2** for data validation and **Motor** for async MongoDB operations. Here's how to work with them effectively:

### Model Structure

The project follows a clean separation between database models and API models:

```python
# Database model (for MongoDB storage)
class TeacherNoteInDB(BaseModel):
    title: str
    description: str
    datePosted: datetime = Field(default_factory=datetime.now)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

# API model (for responses)
class TeacherNote(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    date_posted: Optional[datetime] = Field(default=None, alias="datePosted")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
```

### ObjectId Handling

MongoDB ObjectIds are automatically converted to strings for JSON serialization:

```python
@field_validator('id', mode='before')
@classmethod
def validate_object_id(cls, v: Any) -> Optional[str]:
    """Convert ObjectId to string for JSON serialization"""
    if v is None:
        return None
    if isinstance(v, ObjectId):
        return str(v)  # Automatic conversion
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId string")
    raise ValueError("Invalid ObjectId type")
```

### CRUD Operations with Motor

#### Create Operation
```python
@router.post("/", response_model=TeacherNoteResponse)
async def create_teacher_note(note_data: TeacherNoteCreate):
    db = get_flash_web_database()
    
    # Create document for MongoDB
    new_note = {
        "title": note_data.title.strip(),
        "description": note_data.description.strip(),
        "datePosted": datetime.now(),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    # Insert with Motor
    result = await db.teacher_notes.insert_one(new_note)
    
    # Retrieve and convert for response
    created_note = await db.teacher_notes.find_one({"_id": result.inserted_id})
    return TeacherNoteResponse(success=True, note=teacher_note_helper(created_note))
```

#### Read Operations
```python
# Find multiple documents
cursor = db.teacher_notes.find(query).sort(sort_by, sort_order)
notes = await cursor.to_list(length=None)

# Find single document
note = await db.teacher_notes.find_one({"_id": ObjectId(note_id)})
```

#### Update Operation
```python
# Update with Motor
result = await db.teacher_notes.update_one(
    {"_id": ObjectId(note_id)},
    {"$set": update_data}
)

# Check if document was found
if result.matched_count == 0:
    raise HTTPException(status_code=404, detail="Note not found")
```

#### Delete Operation
```python
result = await db.teacher_notes.delete_one({"_id": ObjectId(note_id)})

if result.deleted_count == 0:
    raise HTTPException(status_code=404, detail="Note not found")
```

### Helper Functions

Use helper functions to convert MongoDB documents to API response format:

```python
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
```

### Database Connection Pattern

Access databases using the convenience functions:

```python
from app.database import get_flash_web_database, get_grade3_database

# In your route functions
@router.get("/teacher_notes")
async def get_notes():
    db = get_flash_web_database()  # Uses flash_web database
    notes = await db.teacher_notes.find({}).to_list(100)
    return [teacher_note_helper(note) for note in notes]

@router.get("/grade3_content")
async def get_grade3_content():
    db = get_grade3_database()  # Uses grade3 database
    content = await db.lessons.find({}).to_list(50)
    return content
```

### Best Practices

1. **Always use helper functions** to convert MongoDB documents to API models
2. **Validate ObjectIds** before using them in queries
3. **Handle Motor exceptions** with proper HTTP status codes
4. **Use field aliases** for MongoDB field names (e.g., `datePosted` vs `date_posted`)
5. **Separate database models from API models** for clean architecture
6. **Use async/await** consistently with Motor operations

### Common MongoDB Document Format

Your MongoDB documents will look like this:
```json
{
  "_id": {"$oid": "697c8d1e21962f9633b12520"},
  "title": "Thông báo (30/1)",
  "description": "<p>GV Tiếng anh dặn dò:</p><p>- HS thiếu sách/vở: Lan Chi</p>",
  "datePosted": {"$date": "2026-01-30T10:51:10.157Z"},
  "createdAt": {"$date": "2026-01-30T10:51:10.157Z"},
  "updatedAt": {"$date": "2026-01-30T10:51:10.157Z"}
}
```

### Troubleshooting

**ObjectId Serialization Issues:**
- Use the `teacher_note_helper()` function to convert documents
- Ensure `@field_validator` is properly configured for ObjectId fields

**Pydantic Validation Errors:**
- Check field aliases match your MongoDB field names
- Use `populate_by_name=True` in model config
- Ensure proper typing with `Optional` for nullable fields

**Motor Connection Issues:**
- Verify your `.env` file has correct MongoDB connection string
- Check that `connect_to_mongo()` is called during app startup
- Use the health endpoint `/health` to verify database connectivity

## Notes

- `requirements.txt` is present but not required for the standard `uv` workflow. Prefer `uv sync` over manual `pip install`.
- If you change dependencies, update `pyproject.toml` and regenerate the lockfile with `uv lock` (or rerun `uv sync` as appropriate).

uv sync && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT