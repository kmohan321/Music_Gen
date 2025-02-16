# AI Music Generator

## Project Overview

This project is an AI-powered music generation tool. It's designed to explore the intersection of artificial intelligence and music, allowing users to generate unique melodies and drum patterns.

## Features

*   **Melody Generation:**
    *   AI-based melody generation using a Long Short-Term Memory (LSTM) network.
    *   Generates music in the style learned from a dataset of music pieces.
    *   Users can influence the generation process through:
        *   **Seed Sequences:** Starting the melody generation with a custom or pre-defined musical phrase.
        *   **Temperature Parameter:** Adjusting the randomness and creativity of the generated melody.
*   **Drum Pattern Generation:**
    *   AI-based drum pattern generation using an LSTM network.
    *   Generates rhythmic drum patterns based on learned styles.
    *   Users can control:
        *   **Sequence Length:** Setting the duration of the generated drum pattern.
        *   **Temperature Parameter:**  Controlling the variability of the drum rhythms.
*   **Web API (Backend):**
    *   Built with FastAPI to serve the music generation models.
    *   Handles requests for melody and drum pattern generation.
    *   Converts generated MIDI data into WAV and MP3 audio formats using `fluidsynth` and `ffmpeg`.
    *   Provides endpoints to access generated audio files and MIDI data.
*   **User Interface (Frontend):**
    *   Developed with React for a user-friendly experience.
    *   Allows users to:
        *   Select between melody and drum generation models.
        *   Adjust generation parameters (seed, temperature, drum length).
        *   Trigger music generation and view loading status.
        *   Play generated audio directly in the browser.
        *   View a history of generated tracks.
        *   Download generated audio files (WAV, MP3) and MIDI data.
        *   Toggle between light and dark themes for user preference.
        *   Visualize audio output with a basic frequency bar visualization.
*   **Output Formats:**
    *   Generates music in MIDI format internally.
    *   Provides output in WAV and MP3 audio formats for easy playback and sharing.
    *   Offers MIDI data in Base64 encoded format for potential further processing or use in other applications.
*   **Visualization:**
    *   Basic audio visualization using HTML5 Canvas to display frequency data while playing audio with beat sync.
*   **Theme Switching:**
    *   Supports both light and dark themes for comfortable use in different environments.
*   **Generation History:**
    *   Keeps a history of generated music tracks for easy access and review.


## Setup Instructions

To run this project, you will need to set up both the backend (FastAPI) and the React frontend.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+:** For the backend and AI models.
*   **Node.js and npm:** For the frontend development.
*   **pip** Python package manager.
*   **FluidSynth:** For MIDI to WAV conversion. Install instructions vary by OS:
    *   **Ubuntu/Debian:** `sudo apt-get install fluidsynth`
    *   **macOS (using Homebrew):** `brew install fluidsynth`
    *   **Windows:** Download from [http://www.fluidsynth.org/](http://www.fluidsynth.org/) and add to your PATH.
*   **FFmpeg:** For WAV to MP3 conversion. Install instructions vary by OS:
    *   **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
    *   **macOS (using Homebrew):** `brew install ffmpeg`
    *   **Windows:** Download from [https://www.ffmpeg.org/](https://www.ffmpeg.org/) and add to your PATH.
*   **(Optional) CUDA and NVIDIA drivers:** If you have an NVIDIA GPU and want to utilize GPU acceleration for model training and inference (recommended for faster performance).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kmohan321/Music_Gen.git
    cd Music_Gen
    ```

2.  **Set up the backend (Python):**

    *   **Using `requirements.txt` (pip):**
        ```bash
        pip install -r requirements.txt
        ```

    * 
3.  **Set up the frontend (React):**
    ```bash
    cd music-gen-frontend 
    npm install
    ```

### Running the Application

1.  **Start the backend (FastAPI):**
    ```bash
    cd backend
    uvicorn main:app --reload
    ```
    This will start the FastAPI server, at `http://127.0.0.1:8000` or `http://localhost:8000`. The `--reload` flag enables automatic server restart upon code changes, useful for development.

2.  **Start the frontend (React):**
    ```bash
    cd music-gen-frontend
    npm run dev
    ```
    This will start the React development server. Typically, the frontend application will be accessible at `http://localhost:5173`.


## Usage

1.  **Select Model Type:** In the web interface, choose either "Melody" or "Drum" from the model type dropdown.
2.  **Adjust Parameters:**
    *   **Melody:**
        *   **Seed:** Choose a pre-defined seed from the dropdown or enter a custom seed sequence.
        *   **Temperature:**  Adjust the temperature slider to control the creativity (higher temperature for more random, lower for more predictable).
    *   **Drum:**
        *   **Drum Length:** Set the desired length of the drum pattern.
        *   **Temperature:** Adjust the temperature slider for drum pattern variation.
3.  **Generate Music:** Click the "Generate Music" button. The application will send a request to the backend, and the AI model will generate music. A loading indicator will be displayed while generation is in progress.
4.  **Listen to the Generated Music:** Once generated, the audio player will load the new track. Click the play button to listen to the generated music.
5.  **Download Music:** You can download the generated music in WAV, MP3, and MIDI formats from the history panel or audio player section.
6.  **Explore History:** The history panel on the right side displays a list of previously generated tracks. You can select a track from history to play it again.
7.  **Theme Toggle:** Use the theme toggle in the top bar to switch between light and dark modes.

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, new features, or bug fixes, please feel free to:

*   **Fork the repository** and create a branch for your changes.
*   **Submit a pull request** with your proposed changes.
*   **Open an issue** to report bugs or suggest new features.

Please ensure your code adheres to the existing style and includes comments where necessary. For significant changes, it's recommended to discuss them in an issue first before submitting a pull request.

## Contact

For questions or further information, please contact the [Robotics Club Name](https://www.linkedin.com/in/robotics-club-mnnit/)

---

**Happy Music Generation!**