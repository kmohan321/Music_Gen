import os
import json
import pretty_midi
import numpy as np

# Paths
MIDI_PATH = r"C:\Users\Krishna Mohan\Downloads\Compressed\groove\drummer7\eval_session"
SINGLE_SONG_PATH = "drum_single_song.txt"
MAP_PATH = "drum_map.json"
SEQUENCE_LENGTH = 128

def load_midi_files(path, max_limit=-1):
    """Load drum MIDI files from a directory."""
    midi_files = []
    for dirpath, _, files in os.walk(path):
        for file in files[:max_limit]:
            if file.endswith('.mid'):
                midi = pretty_midi.PrettyMIDI(os.path.join(dirpath, file))
                midi_files.append(midi)
    return midi_files

def extract_drum_events(midi_files):
    """Extract drum notes from MIDI files."""
    drum_sequences = []
    for midi in midi_files:
        drum_track = [inst for inst in midi.instruments if inst.is_drum]
        if not drum_track:
            continue
        drum_notes = []
        for note in drum_track[0].notes:
            drum_notes.append((note.start, note.pitch))  # (time, drum pad hit)
        drum_notes.sort()  # Ensure events are in chronological order
        drum_sequences.append(drum_notes)
    return drum_sequences

def encode_drum_events(drum_sequences, timestep=0.1):
    """Convert drum notes into a sequence of events at fixed time intervals."""
    encoded_songs = []
    for sequence in drum_sequences:
        encoded_song = []
        last_time = 0.0
        for time, pitch in sequence:
            time_steps = int((time - last_time) / timestep)
            encoded_song.extend(['_'] * time_steps)  # Padding for time gaps
            encoded_song.append(str(pitch))  # Drum note hit
            last_time = time
        encoded_songs.append(" ".join(encoded_song))
    return " ".join(encoded_songs)

def save_encoded_data(encoded_song, path):
    """Save encoded drum sequence to a file."""
    with open(path, 'w') as f:
        f.write(encoded_song)

def create_mapping(encoded_song, map_path):
    """Create a mapping from unique tokens to integers."""
    unique_tokens = sorted(set(encoded_song.split()))
    mapping = {token: i for i, token in enumerate(unique_tokens)}
    with open(map_path, 'w') as f:
        json.dump(mapping, f, indent=4)

def generate_training_samples(sequence_length=SEQUENCE_LENGTH, map_path=MAP_PATH):
    """Generate input-target pairs for training."""
    with open(map_path, 'r') as f:
        mapping = json.load(f)
    with open("drum_single_song.txt","r") as f:
        encoded_song = f.read()
    song_tokens = encoded_song.split()
    mapped_song = [mapping[token] for token in song_tokens]
    
    inputs, targets = [], []
    for i in range(len(mapped_song) - sequence_length):
        inputs.append(mapped_song[i:i+sequence_length])
        targets.append(mapped_song[i+sequence_length])
    
    return np.array(inputs), np.array(targets)

def get_vocab_size(map_path=MAP_PATH):
    """Retrieve the vocabulary size."""
    with open(map_path, 'r') as f:
        mapping = json.load(f)
    return len(mapping)

# Example Usage:
# midi_files = load_midi_files(MIDI_PATH, max_limit=20)
# drum_sequences = extract_drum_events(midi_files)
# encoded_song = encode_drum_events(drum_sequences)
# save_encoded_data(encoded_song, SINGLE_SONG_PATH)
# create_mapping(encoded_song, MAP_PATH)
# inputs, targets = generate_training_samples(encoded_song, SEQUENCE_LENGTH, MAP_PATH)
