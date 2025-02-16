import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  createTheme,
  ThemeProvider,
  CssBaseline,
} from '@mui/material';
import { motion } from 'framer-motion';
import axios from 'axios';

import TopBar from './components/TopBar';
import GenerationControls from './components/GenerationControls';
import AudioPlayer from './components/AudioPlayer';
import HistoryPanel from './components/HistoryPanel';

function App() {
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

  const darkModeRef = useRef(darkMode);
  useEffect(() => {
    darkModeRef.current = darkMode;
  }, [darkMode]);

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

  const [modelType, setModelType] = useState('Melody');
  const [seed, setSeed] = useState(seedOptions.seed2);
  const [temperature, setTemperature] = useState(1.7);
  const [drumLength, setDrumLength] = useState(256);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [history, setHistory] = useState([]);
  const [currentTrack, setCurrentTrack] = useState(null);

  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const bufferLengthRef = useRef(null);

  useEffect(() => {

    const setupVisualization = () => {
      const audio = audioRef.current;
      const canvas = canvasRef.current;

      if (!audio || !canvas) {
        setTimeout(setupVisualization, 100);
        return;
      }

      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 64;
        bufferLengthRef.current = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLengthRef.current);

        const source = audioContextRef.current.createMediaElementSource(audio);
        source.connect(analyserRef.current);
        analyserRef.current.connect(audioContextRef.current.destination);
      } else {
        console.log("setupVisualization: AudioContext already initialized");
      }

      const canvasCtx = canvas.getContext("2d");
      if (!canvasCtx) {
        console.error("setupVisualization: Canvas context is null!");
        return;
      }
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;

      const draw = () => {
        if (!analyserRef.current || !canvasCtx || !dataArrayRef.current) {
          console.log("draw: Analyser, context, or dataArray NOT ready, exiting draw");
          return;
        }
        requestAnimationFrame(draw);
        analyserRef.current.getByteFrequencyData(dataArrayRef.current);

        // Visualization drawing logic (same as before)
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

    setupVisualization();

  }, [darkMode]);

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
          wavFilename: data.wav_filename,
          mp3Filename: data.mp3_filename,
          midiData: `data:audio/midi;base64,${data.midi_base64}`,
          timestamp: new Date().toLocaleString(),
        };

        setHistory((prev) => [newTrack, ...prev]);
        setCurrentTrack(newTrack);
        console.log("handleGenerate: New track set:", newTrack);
      }
    } catch (err) {
      console.error(err);
      setError('Error generating music');
    }
    setLoading(false);
  };

  const togglePlay = () => {
    console.log("togglePlay: isPlaying before toggle:", isPlaying);
    if (!audioRef.current) {
      console.log("togglePlay: audioRef.current is null, exiting");
      return;
    }
    if (isPlaying) {
      console.log("togglePlay: Pausing audio");
      audioRef.current.pause();
    } else {
      console.log("togglePlay: Playing audio, audioContext state:", audioContextRef.current?.state);
      if (audioContextRef.current && audioContextRef.current.state === 'suspended') {
        audioContextRef.current.resume();
        console.log("togglePlay: AudioContext resumed");
      }
      audioRef.current.play().catch(e => console.error("Audio play failed:", e));
    }
    setIsPlaying((prev) => !prev);
    console.log("togglePlay: isPlaying after toggle:", !isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setProgress(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
      console.log("handleLoadedMetadata: Duration loaded:", audioRef.current.duration);
    }
  };

  const handleSeek = (event, newValue) => {
    console.log("handleSeek: Seek to time:", newValue);
    if (audioRef.current) {
      audioRef.current.currentTime = newValue;
      setProgress(newValue);
      console.log("handleSeek: Audio currentTime set to:", newValue);
    }
  };

  useEffect(() => {
    if (currentTrack) {
      console.log("useEffect [currentTrack]: currentTrack changed:", currentTrack);
      if (audioRef.current) {
        setIsPlaying(false);
        setProgress(0);
        console.log("useEffect [currentTrack]: Audio loaded, isPlaying reset, progress reset");
      } else {
        console.log("useEffect [currentTrack]: audioRef is null, cannot load audio");
      }
    } else {
      console.log("useEffect [currentTrack]: currentTrack is null, doing nothing");
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
        <TopBar darkMode={darkMode} toggleTheme={toggleTheme} />

        <Box sx={{ flexGrow: 1, p: 2 }}>
          <Box
            sx={{
              display: 'flex',
              gap: 2,
              height: 'calc(100vh - 100px)',
            }}
          >
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
              {/* Hidden audio element */}
              {currentTrack && (
                <audio
                  ref={audioRef}
                  src={`http://localhost:8000/audio/${currentTrack.wavFilename}`} // Use wavFilename
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                  onEnded={() => setIsPlaying(false)}
                  style={{ width: '100%', marginTop: 10, display: 'none' }}
                  crossOrigin="anonymous"
                />
              )}
            </motion.div>

            {/* History Panel */}
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