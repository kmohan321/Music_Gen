import React from 'react';
import {
  Box,
  Typography,
  IconButton,
  Slider,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import FastForwardIcon from '@mui/icons-material/FastForward';
import FastRewindIcon from '@mui/icons-material/FastRewind';

function AudioPlayer({
  currentTrack,
  isPlaying,
  progress,
  duration,
  audioRef,
  canvasRef,
  togglePlay,
  handleTimeUpdate,
  handleLoadedMetadata,
  handleSeek,
  formatTime,
  setIsPlaying,
  setProgress,
  setDuration,
  darkMode,
}) {

  return (
    <Box
      sx={{
        backgroundColor: darkMode ? '#333' : '#fafafa',
        border: '1px solid',
        borderColor: darkMode ? '#444' : '#e0e0e0',
        borderRadius: 1,
        p: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Typography variant="h6" gutterBottom>
        Audio Player
      </Typography>
      {currentTrack ? (
        <>
          <Typography variant="subtitle1" gutterBottom>
            {currentTrack.timestamp}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <IconButton
              onClick={() => {
                if (audioRef.current) {
                  audioRef.current.currentTime = Math.max(audioRef.current.currentTime - 10, 0);
                }
              }}
            >
              <FastRewindIcon />
            </IconButton>
            <IconButton onClick={togglePlay}>
              {isPlaying ? <PauseIcon fontSize="large" /> : <PlayArrowIcon fontSize="large" />}
            </IconButton>
            <IconButton
              onClick={() => {
                if (audioRef.current) {
                  audioRef.current.currentTime = Math.min(audioRef.current.currentTime + 10, duration);
                }
              }}
            >
              <FastForwardIcon />
            </IconButton>
          </Box>
          {/* Beat Visualization Canvas */}
          <Box
            sx={{
              width: '100%',
              border: '1px solid',
              borderColor: darkMode ? '#555' : '#ddd',
              mb: 2,
            }}
          >
            <canvas ref={canvasRef} style={{ width: '100%', height: '150px' }} />
          </Box>
          {/* Time Slider */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2, width: '100%' }}>
            <Typography variant="caption">{formatTime(progress)}</Typography>
            <Slider
              value={progress}
              min={0}
              max={duration}
              onChange={handleSeek}
              onMouseUp={() => { }}
              onTouchEnd={() => { }}
              sx={{ flex: 1 }}
            />
            <Typography variant="caption">{formatTime(duration)}</Typography>
          </Box>
        </>
      ) : (
        <Typography variant="body1" sx={{ mt: 'auto' }}>
          No track selected
        </Typography>
      )}
    </Box>
  );
}

export default AudioPlayer;