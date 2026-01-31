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
 
 ## Notes
 
 - `requirements.txt` is present but not required for the standard `uv` workflow. Prefer `uv sync` over manual `pip install`.
 - If you change dependencies, update `pyproject.toml` and regenerate the lockfile with `uv lock` (or rerun `uv sync` as appropriate).


uv sync && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT