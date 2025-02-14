import os
import subprocess
import tempfile
import base64
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import your music generation functions
from Final_Final.generator import Malody_Generator, save_melody, seed_dict
from drum.drum_gen import DrumGenerator

app = FastAPI(title="AI Music Generator API")

# Configure CORS first!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
AUDIO_FILES_DIR = "static/audio"
os.makedirs(AUDIO_FILES_DIR, exist_ok=True)

def midi_to_wav(midi_path, wav_path):
    """Convert MIDI to WAV using fluidsynth"""
    sf_path = os.path.abspath("FluidR3_GM.sf2")
    command = [
        'fluidsynth', '-ni', sf_path, midi_path,
        '-F', wav_path, '-r', '44100', '-T', 'wav'
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Fluidsynth error: {e.stderr.decode()}"
        print(error_msg)
        raise RuntimeError(error_msg)

def wav_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3 using ffmpeg"""
    command = [
        'ffmpeg', '-y', '-i', wav_path,
        '-codec:a', 'libmp3lame', '-qscale:a', '2', mp3_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg error: {e.stderr.decode()}"
        print(error_msg)
        raise RuntimeError(error_msg)

class MusicRequest(BaseModel):
    model_type: str  # "Melody" or "Drum"
    temperature: float = 1.0
    seed: str = None
    drum_length: int = None

class MusicResponse(BaseModel):
    wav_filename: str = None
    mp3_filename: str = None
    midi_base64: str = None
    error: str = None

@app.post("/generate", response_model=MusicResponse)
async def generate_music(request: MusicRequest):
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Generate MIDI
            if request.model_type == "Melody":
                seed_text = request.seed or seed_dict.get("seed1", "_ 67 _ 65 _ 64 _ 62 _ 60 _")
                melody = Malody_Generator(
                    seed=seed_text,
                    num_steps=200,
                    sequence_length=128,
                    temperature=request.temperature
                )
                # Create unique MIDI filename
                midi_filename = f"melody_{uuid.uuid4().hex}.mid"
                midi_path = os.path.join(tmp_dir, midi_filename)
                
                # Verify path is correct
                print(f"Saving melody to: {midi_path}")  # Debug log
                
                save_melody(melody, file_name=midi_path)
                
                # Verify file exists
                if not os.path.exists(midi_path):
                    raise RuntimeError("MIDI file was not created")

            elif request.model_type == "Drum":
                drum_generator = DrumGenerator(
                    model_path='drum/model_drum.pth',
                    map_path='drum/drum_map.json'
                )
                sequence = drum_generator.generate_sequence(
                    length=request.drum_length or 256,
                    temperature=request.temperature
                )
                midi_path = os.path.join(tmp_dir, "generated_drums.mid")
                drum_generator.save_to_midi(sequence, midi_path)
            else:
                raise HTTPException(status_code=400, detail="Invalid model type")

            # Convert to WAV and MP3
            base_name = f"generated_{int(time.time())}_{uuid.uuid4().hex}"
            wav_path = os.path.join(tmp_dir, f"{base_name}.wav")
            mp3_path = os.path.join(tmp_dir, f"{base_name}.mp3")

            midi_to_wav(midi_path, wav_path)
            wav_to_mp3(wav_path, mp3_path)

            # Save to permanent storage
            final_wav_path = os.path.join(AUDIO_FILES_DIR, f"{base_name}.wav")
            final_mp3_path = os.path.join(AUDIO_FILES_DIR, f"{base_name}.mp3")
            
            os.rename(wav_path, final_wav_path)
            os.rename(mp3_path, final_mp3_path)

            # Read MIDI data
            with open(midi_path, "rb") as f:
                midi_data = base64.b64encode(f.read()).decode()

            return MusicResponse(
                wav_filename=f"{base_name}.wav",
                mp3_filename=f"{base_name}.mp3",
                midi_base64=midi_data,
                error=""
            )

    except Exception as e:
        return MusicResponse(error=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_FILES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Validate file type
    if not filename.endswith(('.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)