// src/App.jsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  createTheme,
  ThemeProvider,
  CssBaseline,
} from '@mui/material';
import { motion } from 'framer-motion';
import axios from 'axios';

// Import created components
import TopBar from './components/TopBar';
import GenerationControls from './components/GenerationControls';
import AudioPlayer from './components/AudioPlayer';
import HistoryPanel from './components/HistoryPanel';

function App() {
  // Theme toggling state
  const [darkMode, setDarkMode] = useState(false);
  const toggleTheme = () => setDarkMode((prev) => !prev);
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: { main: darkMode ? '#88c0d0' : '#5e81ac' },
      secondary: { main: darkMode ? '#a3be8c' : '#bf616a' },
      background: { default: darkMode ? '#121212' : '#ffffff' },
    },
    transitions: { duration: { standard: 300 } },
  });

  // Ref to hold current darkMode value for useEffect closures
  const darkModeRef = useRef(darkMode);
  useEffect(() => {
    darkModeRef.current = darkMode;
  }, [darkMode]);

  // Seed dictionary for melody generation
  const seedOptions = {
    seed1: "_ 60 _ _ _ 55 _ _ _ 65 _",
    seed2: "_ 67 _ 65 _ 64 _ 62 _ 60 _",
    seed3: "_ 69 _ 65 _ 67 _ 69 _ 67 _ 65 _ 64 _",
    seed4: "64 _ 69 _ _ _ 71 _ 72 _ _ 71",
    seed5: "_ 67 _ 64 _ 60 _ _ R 76 _",
    seed6: "71 _ _ 69 68 _ 69 _ _ _ _ _ R _ _ _",
    seed7: "_ 62 _ _ _ R _ _ _ 55 _ _ _ 67 _ _ _ 67 _",
    seed8: "_ 62 _ _ _ _ _ 60 _ 60 _ _ _ 55 _",
  };

  // Generation controls state
  const [modelType, setModelType] = useState('Melody');
  const [seed, setSeed] = useState(seedOptions.seed2);
  const [temperature, setTemperature] = useState(1.7);
  const [drumLength, setDrumLength] = useState(256);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // History list state
  const [history, setHistory] = useState([]);
  // Currently selected track
  const [currentTrack, setCurrentTrack] = useState(null);

  // Audio player state and refs
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const bufferLengthRef = useRef(null);

  // Visualization effect - remains in App.jsx as it directly uses audio and canvas refs which are managed here
  useEffect(() => {
    console.log("Visualization useEffect: Entered");

    const setupVisualization = () => {
      console.log("setupVisualization: Running deferred setup");
      if (!audioRef.current || !canvasRef.current) {
        console.log("setupVisualization: refs NOT ready even in deferred setup, exiting");
        return;
      }
      console.log("setupVisualization: refs ARE ready in deferred setup, proceeding");

      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 64;
        bufferLengthRef.current = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLengthRef.current);

        const source = audioContextRef.current.createMediaElementSource(audioRef.current);
        source.connect(analyserRef.current);
        analyserRef.current.connect(audioContextRef.current.destination);

        console.log("AudioContext, Analyser, SourceNode created and connected");
      } else {
        console.log("AudioContext, Analyser already initialized, reusing");
      }


      const canvas = canvasRef.current;
      const canvasCtx = canvas.getContext("2d");
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;


      const draw = () => {
        if (!analyserRef.current || !canvasCtx || !dataArrayRef.current) return;
        requestAnimationFrame(draw);

        analyserRef.current.getByteFrequencyData(dataArrayRef.current);

        const grad = canvasCtx.createLinearGradient(0, 0, canvas.width, canvas.height);
        if (darkModeRef.current) {
          grad.addColorStop(0, "#1e1e1e");
          grad.addColorStop(1, "#444");
        } else {
          grad.addColorStop(0, "#fff");
          grad.addColorStop(1, "#f0f0f0");
        }
        canvasCtx.fillStyle = grad;
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

        const barWidth = canvas.width / bufferLengthRef.current;
        for (let i = 0; i < bufferLengthRef.current; i++) {
          const barHeight = dataArrayRef.current[i] * 1.5;
          canvasCtx.fillStyle = `hsl(${(i / bufferLengthRef.current) * 360}, ${darkModeRef.current ? 80 : 60}%, ${darkModeRef.current ? 50 : 40}%)`;
          canvasCtx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 2, barHeight);
        }
      };

      draw();
    };

    setTimeout(setupVisualization, 0);

  }, []);

  // Function to handle music generation API call - remains in App.jsx as it manages app-level state (history, currentTrack, loading, error)
  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/generate', {
        model_type: modelType,
        temperature: temperature,
        seed: modelType === 'Melody' ? seed : undefined,
        drum_length: modelType === 'Drum' ? drumLength : undefined,
      });
      const data = response.data;
      if (data.error) {
        setError(data.error);
      } else {
        const newTrack = {
          id: Date.now(),
          audioSrc: `http://localhost:8000/audio/${data.audio_filename}`, // Audio URL from backend
          midiData: `data:audio/midi;base64,${data.midi_base64}`,
          timestamp: new Date().toLocaleString(),
        };
        setHistory((prev) => [newTrack, ...prev]);
        setCurrentTrack(newTrack);
      }
    } catch (err) {
      console.error(err);
      setError('Error generating music');
    }
    setLoading(false);
  };

  // Audio player functions - mostly passed down to AudioPlayer component, some state management remains here
  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      if (audioContextRef.current && audioContextRef.current.state === 'suspended') {
        audioContextRef.current.resume();
      }
      audioRef.current.play();
    }
    setIsPlaying((prev) => !prev);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setProgress(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (event, newValue) => {
    if (audioRef.current) {
      audioRef.current.currentTime = newValue;
      setProgress(newValue);
    }
  };

  useEffect(() => {
    if (currentTrack && audioRef.current) {
      audioRef.current.load();
      setIsPlaying(false);
      setProgress(0);
    }
  }, [currentTrack]);

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };


  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          width: '100vw',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          background: darkMode
            ? 'linear-gradient(135deg, #121212, #1d1d1d)'
            : 'linear-gradient(135deg, #f0f4ff, #cfd9df)',
          transition: 'background 0.5s ease-in-out',
        }}
      >
        {/* Top Bar Component */}
        <TopBar darkMode={darkMode} toggleTheme={toggleTheme} />

        {/* Main Content Container */}
        <Box sx={{ flexGrow: 1, p: 2 }}>
          <Box
            sx={{
              display: 'flex',
              gap: 2,
              height: 'calc(100vh - 100px)', // Adjust height based on TopBar height
            }}
          >
            {/* Generation Controls Panel Component */}
            <motion.div style={{ flex: '1 1 300px', minWidth: '300px', height: '100%' }}>
              <GenerationControls
                modelType={modelType}
                setModelType={setModelType}
                seed={seed}
                setSeed={setSeed}
                temperature={temperature}
                setTemperature={setTemperature}
                drumLength={drumLength}
                setDrumLength={setDrumLength}
                loading={loading}
                error={error}
                handleGenerate={handleGenerate}
                seedOptions={seedOptions}
                darkMode={darkMode}
              />
            </motion.div>

            {/* Audio Player Panel Component */}
            <motion.div style={{ flex: '2 1 400px', minWidth: '400px', height: '100%' }}>
              <AudioPlayer
                currentTrack={currentTrack}
                isPlaying={isPlaying}
                progress={progress}
                duration={duration}
                audioRef={audioRef}
                canvasRef={canvasRef}
                togglePlay={togglePlay}
                handleTimeUpdate={handleTimeUpdate}
                handleLoadedMetadata={handleLoadedMetadata}
                handleSeek={handleSeek}
                formatTime={formatTime}
                setIsPlaying={setIsPlaying}
                setProgress={setProgress}
                setDuration={setDuration}
                darkMode={darkMode}
              />
              {/* Hidden audio element - remains in App.jsx to be accessible by refs and state */}
              <audio
                ref={audioRef}
                src={currentTrack?.audioSrc || ""} // Use optional chaining in case currentTrack is null
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={() => setIsPlaying(false)}
                style={{ width: '100%', marginTop: 10, display: 'none' }}
              />
            </motion.div>

            {/* History Panel Component */}
            <motion.div style={{ flex: '1 1 300px', minWidth: '300px', height: '100%' }}>
              <HistoryPanel
                history={history}
                currentTrack={currentTrack}
                setCurrentTrack={setCurrentTrack}
                darkMode={darkMode}
              />
            </motion.div>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;