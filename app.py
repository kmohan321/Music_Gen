import streamlit as st
import music21 as m21
import tempfile
import os
import sys
import torch
from Final_Final.generator import Malody_Generator, save_melody, seed_dict
from drum.drum_gen import DrumGenerator  # New import

# Configure paths
sys.path.append(os.path.join(os.path.dirname(__file__), "Final_Final"))
sys.path.append(os.path.join(os.path.dirname(__file__), "drum"))

def midi_to_wav(midi_path, wav_path):
    """Convert MIDI to WAV using music21's built-in synthesizer"""
    midi = m21.converter.parse(midi_path)
    sf_path = m21.environment.Environment()['soundfont']
    if sf_path is None:
        raise ValueError("No SoundFont configured. Please install MuseScore and set the MUSESCORE_PATH environment variable.")
    midi.synth().write(wav_path)

def main():
    st.title("🎵 AI Music Generator")
    
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
                    if model_type == "Melody":
                        # Melody generation
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
                        # Drum generation
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

                    # Common output handling
                    try:
                        midi_to_wav(midi_path, wav_path)
                        st.success("🎉 Composition Complete!")
                        st.audio(wav_path, format='audio/wav')
                    except Exception as e:
                        st.warning("Couldn't generate audio preview. MIDI download is still available.")
                        st.error(f"Audio conversion error: {str(e)}")

                    # Download button
                    with open(midi_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Download MIDI File",
                            data=file,
                            file_name="generated.mid",
                            mime="audio/midi"
                        )

            except Exception as e:
                st.error(f"Error generating music: {str(e)}")

if __name__ == "__main__":
    main()