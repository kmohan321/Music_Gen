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
    print(f"midi_to_wav: Running command: {command}") # LOGGING - Add this
    try:
        completed_process = subprocess.run(command, check=True, shell=True, capture_output=True) # Capture output
        print(f"midi_to_wav: Fluidsynth completed successfully.") # LOGGING - Add this
        if completed_process.stderr: # Check for stderr even on success
            print(f"midi_to_wav: Fluidsynth stderr: {completed_process.stderr.decode()}") # LOGGING
    except subprocess.CalledProcessError as e:
        error_message = f"Fluidsynth error: {e.stderr.decode()}"
        print(f"midi_to_wav: ERROR - {error_message}") # LOGGING - Add this
        raise RuntimeError(error_message)
    except FileNotFoundError:
        error_message = "Error: fluidsynth executable not found. Is it installed and in your PATH?"
        print(f"midi_to_wav: ERROR - {error_message}") # LOGGING
        raise RuntimeError(error_message)
def wav_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3 using ffmpeg"""
    command = f'ffmpeg -i "{wav_path}" -codec:a libmp3lame -qscale:a 2 "{mp3_path}"'
    try:
        subprocess.run(command, check=True, shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        error_message = f"FFmpeg error: {e.stderr.decode()}"
        print(f"wav_to_mp3: ERROR - {error_message}")
        raise RuntimeError(error_message)
    
# Request payload for generating music.
class MusicRequest(BaseModel):
    model_type: str  # Either "Melody" or "Drum"
    temperature: float = 1.0
    seed: str = None         # Only used for melody generation
    drum_length: int = None  # Only used for drum generation

# Response payload.
class MusicResponse(BaseModel):
    audio_filename: str = None  # WAV filename
    mp3_filename: str = None    # Add this
    midi_base64: str = None
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
    print(f"get_audio_file: Attempting to serve file: {audio_filepath}") # LOGGING - Add this
    if not os.path.exists(audio_filepath):
        print(f"get_audio_file: File NOT FOUND: {audio_filepath}") # LOGGING - Add this
        raise HTTPException(status_code=404, detail="Audio file not found")
    print(f"get_audio_file: File FOUND, serving: {audio_filepath}") # LOGGING - Add this
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