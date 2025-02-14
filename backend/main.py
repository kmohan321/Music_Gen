import os
import subprocess
import tempfile
import base64
import time
import uuid  # For generating unique filenames
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import your music generation functions.
# Adjust these imports and paths as needed.
from Final_Final.generator import Malody_Generator, save_melody, seed_dict
from drum.drum_gen import DrumGenerator

app = FastAPI(title="AI Music Generator API")

# --- Configuration ---
AUDIO_FILES_DIR = "static/audio"  # Directory to save audio files
STATIC_MP3_FILE = "test.mp3"      # Static MP3 file name (place test.mp3 next to main.py)

# Ensure the audio files directory exists
os.makedirs(AUDIO_FILES_DIR, exist_ok=True)

def midi_to_wav(midi_path, wav_path):
    """Convert a MIDI file to WAV using fluidsynth."""
    sf_path = os.path.abspath("FluidR3_GM.sf2")
    command = f'fluidsynth -ni "{sf_path}" "{midi_path}" -F "{wav_path}" -r 44100 -T wav'
    try:
        subprocess.run(command, check=True, shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Fluidsynth error: {e.stderr.decode()}")

# Request payload for generating music.
class MusicRequest(BaseModel):
    model_type: str  # Either "Melody" or "Drum"
    temperature: float = 1.0
    seed: str = None         # Only used for melody generation
    drum_length: int = None  # Only used for drum generation

# Response payload.
class MusicResponse(BaseModel):
    audio_filename: str = None  # Filename of the generated audio file (to be used in URL)
    midi_base64: str = None   # Base64 encoded MIDI file
    error: str = None

@app.post("/generate", response_model=MusicResponse)
def generate_music(request: MusicRequest):
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # --- Generate music based on model type ---
            if request.model_type == "Melody":
                # Use a default seed if none provided.
                seed_text = request.seed or seed_dict.get("seed1", "_ 67 _ 65 _ 64 _ 62 _ 60 _")
                melody = Malody_Generator(
                    seed=seed_text,
                    num_steps=200,
                    sequence_length=128,
                    temperature=request.temperature
                )
                midi_path = os.path.join(tmp_dir, "generated.mid")
                wav_path = os.path.join(tmp_dir, "output.wav")
                save_melody(melody, file_name=midi_path)
            elif request.model_type == "Drum":
                drum_length = request.drum_length or 256
                drum_generator = DrumGenerator(
                    model_path='drum/model_drum.pth',
                    map_path='drum/drum_map.json'
                )
                sequence = drum_generator.generate_sequence(length=drum_length, temperature=request.temperature)
                midi_path = os.path.join(tmp_dir, "generated_drums.mid")
                wav_path = os.path.join(tmp_dir, "output.wav")
                drum_generator.save_to_midi(sequence, midi_path)
            else:
                raise HTTPException(status_code=400, detail="Invalid model type")

            # --- Convert MIDI to WAV and Read generated files ---
            with open(midi_path, "rb") as f:
                midi_bytes = f.read()
            midi_base64_encoded = base64.b64encode(midi_bytes).decode("utf-8")

            try:
                midi_to_wav(midi_path, wav_path)
                with open(wav_path, "rb") as f:
                    wav_bytes = f.read()
                wav_base64_encoded = base64.b64encode(wav_bytes).decode("utf-8")

                # --- Save WAV file to static directory ---
                audio_filename = f"generated_{int(time.time())}_{uuid.uuid4()}.wav" # Unique filename
                audio_filepath = os.path.join(AUDIO_FILES_DIR, audio_filename)
                with open(audio_filepath, "wb") as audio_file:
                    audio_file.write(wav_bytes) # Save WAV bytes to file

            except Exception as e:
                # Return MIDI and error even if audio conversion fails.
                return MusicResponse(
                    audio_filename=None, # No audio file served if conversion failed
                    midi_base64=midi_base64_encoded,
                    error=str(e)
                )

            return MusicResponse(
                audio_filename=audio_filename, # Return filename for frontend to construct URL
                midi_base64=midi_base64_encoded,
                error=""
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve audio files from the static audio directory."""
    audio_filepath = os.path.join(AUDIO_FILES_DIR, filename)
    if not os.path.exists(audio_filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_filepath, headers={"Access-Control-Allow-Origin": "http://localhost:5173"})

@app.get("/test_audio")
async def get_test_audio():
    """Serve a static test MP3 audio file."""
    test_audio_filepath = os.path.join(AUDIO_FILES_DIR, STATIC_MP3_FILE)
    if not os.path.exists(test_audio_filepath):
        raise HTTPException(status_code=404, detail="Test audio file not found. Place 'test.mp3' in the 'static/audio' directory.")
    return FileResponse(test_audio_filepath)

if __name__ == "__main__":
    import uvicorn
    # Run with: python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# Enable CORS - Corrected and made explicit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Be explicit about methods
    allow_headers=["Content-Type", "Authorization"], # Be explicit about headers if needed
)