# app.py
import streamlit as st
from generator import Malody_Generator, save_melody, seed_dict
import music21 as m21
import tempfile
import os

def midi_to_wav(midi_path, wav_path):
    """Convert MIDI to WAV using music21's built-in synthesizer"""
    midi = m21.converter.parse(midi_path)
    sp = midi.write('midi')
    sf_path = m21.environment.Environment()['soundfont']
    if sf_path is None:
        raise ValueError("No SoundFont configured. Please install MuseScore and set the MUSESCORE_PATH environment variable.")
    
    # Synthesize MIDI to WAV
    midi.synth().write(wav_path)

def main():
    st.title("🎵 AI Music Generator")
    
    # Sidebar controls
    st.sidebar.header("Generation Settings")
    
    # Seed selection
    selected_seed = st.sidebar.selectbox(
        "Choose a seed melody:",
        options=list(seed_dict.keys()),
        index=1
    )
    
    # Temperature control
    temperature = st.sidebar.slider(
        "Temperature (Creativity Control)",
        min_value=0.1,
        max_value=2.5,
        value=1.7,
        step=0.1
    )
    
    # Generation button
    if st.sidebar.button("✨ Generate Music"):
        with st.spinner("Composing your masterpiece..."):
            try:
                # Generate melody
                melody = Malody_Generator(
                    seed=seed_dict[selected_seed],
                    num_steps=200,
                    sequence_length=128,
                    temperature=temperature
                )
                
                # Create temporary files
                with tempfile.TemporaryDirectory() as tmp_dir:
                    midi_path = os.path.join(tmp_dir, "generated.mid")
                    wav_path = os.path.join(tmp_dir, "output.wav")
                    
                    # Save MIDI file
                    save_melody(melody, file_name=midi_path)
                    
                    try:
                        # Convert to WAV for playback
                        midi_to_wav(midi_path, wav_path)
                        
                        # Display audio player
                        st.success("🎉 Composition Complete!")
                        st.audio(wav_path, format='audio/wav')
                        
                    except Exception as e:
                        st.warning("Couldn't generate audio preview. MIDI download is still available.")
                        st.error(f"Audio conversion error: {str(e)}")
                    
                    # Display download button
                    with open(midi_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Download MIDI File",
                            data=file,
                            file_name="generated_melody.mid",
                            mime="audio/midi"
                        )

            except Exception as e:
                st.error(f"Error generating music: {str(e)}")

if __name__ == "__main__":
    main()