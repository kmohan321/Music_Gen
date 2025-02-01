import streamlit as st
import music21 as m21
import tempfile
import os
import sys
import time
from Final_Final.generator import Malody_Generator, save_melody, seed_dict
from drum.drum_gen import DrumGenerator

# Configure paths
sys.path.append(os.path.join(os.path.dirname(__file__), "Final_Final"))
sys.path.append(os.path.join(os.path.dirname(__file__), "drum"))

def midi_to_wav(midi_path, wav_path):
    """Fallback conversion using fluidsynth"""
    import subprocess
    
    sf_path = os.path.abspath("FluidR3_GM.sf2")
    command = f'fluidsynth -ni "{sf_path}" "{midi_path}" -F "{wav_path}" -r 44100 -T wav'
    
    try:
        subprocess.run(command, check=True, shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Fluidsynth error: {e.stderr.decode()}")
    
def main():
    st.title("🎵 AI Music Generator")
    
    # Initialize session state for history
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Sidebar controls
    st.sidebar.header("Generation Settings")
    
    # Model type selection
    model_type = st.sidebar.radio(
        "Select Model Type:",
        ("Melody", "Drum"),
        index=0
    )
    
    # Common parameters
    temperature = st.sidebar.slider(
        "Temperature (Creativity Control)",
        min_value=0.1,
        max_value=2.5,
        value=1.7,
        step=0.1
    )
    
    # Model-specific parameters
    if model_type == "Melody":
        selected_seed = st.sidebar.selectbox(
            "Choose a seed melody:",
            options=list(seed_dict.keys()),
            index=1
        )
    else:
        drum_length = st.sidebar.slider(
            "Drum Sequence Length",
            min_value=50,
            max_value=500,
            value=256,
            step=50
        )

    if st.sidebar.button("✨ Generate Music"):
        with st.spinner("Composing your masterpiece..."):
            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    # Generate content
                    if model_type == "Melody":
                        melody = Malody_Generator(
                            seed=seed_dict[selected_seed],
                            num_steps=200,
                            sequence_length=128,
                            temperature=temperature
                        )
                        midi_path = os.path.join(tmp_dir, "generated.mid")
                        wav_path = os.path.join(tmp_dir, "output.wav")
                        save_melody(melody, file_name=midi_path)
                    else:
                        drum_generator = DrumGenerator(
                            model_path='drum/model_drum.pth',
                            map_path='drum/drum_map.json'
                        )
                        sequence = drum_generator.generate_sequence(
                            length=drum_length,
                            temperature=temperature
                        )
                        midi_path = os.path.join(tmp_dir, "generated_drums.mid")
                        wav_path = os.path.join(tmp_dir, "output.wav")
                        drum_generator.save_to_midi(sequence, midi_path)

                    # Read files before tempdir cleanup
                    with open(midi_path, "rb") as f:
                        midi_bytes = f.read()
                    
                    try:
                        midi_to_wav(midi_path, wav_path)
                        with open(wav_path, "rb") as f:
                            wav_bytes = f.read()
                        error = None
                    except Exception as e:
                        wav_bytes = None
                        error = str(e)

                    # Add to history (newest first)
                    st.session_state.history.insert(0, {
                        'timestamp': time.time(),
                        'model_type': model_type,
                        'wav_bytes': wav_bytes,
                        'midi_bytes': midi_bytes,
                        'error': error
                    })

                    # Keep only last 5 entries
                    if len(st.session_state.history) > 5:
                        st.session_state.history = st.session_state.history[:5]

            except Exception as e:
                st.error(f"Error generating music: {str(e)}")

    # Display history
    for entry in st.session_state.history:
        with st.container():
            st.write(f"**{entry['model_type']} Track** (Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['timestamp']))})")
            
            if entry['error']:
                st.warning("Couldn't generate audio preview. MIDI download is still available.")
                st.error(f"Audio conversion error: {entry['error']}")
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.audio(entry['wav_bytes'], format='audio/wav')
                with col2:
                    st.download_button(
                        label="⬇️ Download MIDI",
                        data=entry['midi_bytes'],
                        file_name="generated.mid",
                        mime="audio/midi",
                        key=f"dl_{entry['timestamp']}"
                    )
            st.markdown("---")

if __name__ == "__main__":
    main()