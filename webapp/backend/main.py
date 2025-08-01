import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid # For unique filenames

# Add the parent directory of src to the Python path to import generate
# This assumes the webapp/backend is one level below the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(project_root, 'src', 'generation'))

try:
    from generate import generate_music
except ImportError as e:
    raise RuntimeError(f"Could not import generate_music. Make sure src/generation is in PYTHONPATH. Error: {e}")

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000", # Default FastAPI/Uvicorn port
    "http://localhost:8080", # Common frontend development port
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5500", # Common Live Server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

class GenerateRequest(BaseModel):
    genre: str
    seed_notes: str
    temperature: float = 1.0
    generation_length: int = 500 # Add generation_length with a default value

@app.post("/generate_solo")
async def generate_solo_endpoint(request: GenerateRequest):
    try:
        # Create a unique filename for the generated MIDI
        output_filename = f"{request.genre.lower()}_solo_{uuid.uuid4()}.mid"
        output_path = os.path.join(project_root, "output", output_filename)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Call the generation function, passing the temperature and generation_length
        generate_music(
            genre=request.genre,
            seed_notes_str=request.seed_notes,
            output_path=output_path,
            temperature=request.temperature,
            generation_length=request.generation_length # Pass the generation_length here
        )

        # Return the generated MIDI file with Content-Disposition header
        return FileResponse(output_path, media_type="audio/midi", filename=output_filename, headers={"Content-Disposition": f"attachment; filename=\"{output_filename}\""})



    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during solo generation: {e}")

@app.get("/hello")
async def read_root():
    return {"message": "Hello from FastAPI backend!"}
