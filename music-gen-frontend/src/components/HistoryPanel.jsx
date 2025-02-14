// src/components/HistoryPanel.jsx
import React from 'react';
import { Box, Typography, Button, Stack } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

/**
 * HistoryPanel component to display and manage the history of generated music tracks.
 *
 * @param {object} props - Component props.
 * @param {Array<object>} props.history - Array of generated music track objects.
 * @param {object | null} props.currentTrack - Currently selected music track object.
 * @param {function} props.setCurrentTrack - Function to set the currently selected track.
 * @param {boolean} props.darkMode - Current dark mode state for styling.
 */
function HistoryPanel({ history, currentTrack, setCurrentTrack, darkMode }) {
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
      }}
    >
      <Typography variant="h6" gutterBottom>
        History
      </Typography>
      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        {history.length === 0 ? (
          <Typography variant="body2">No history available.</Typography>
        ) : (
          history.map((track) => (
            <Box
              key={track.id}
              sx={{
                p: 1,
                mb: 1,
                border: '1px solid',
                borderColor:
                  currentTrack && currentTrack.id === track.id ? 'primary.main' : 'divider',
                borderRadius: 0,
                cursor: 'pointer',
                transition: 'transform 0.3s',
                '&:hover': { transform: 'scale(1.02)' },
              }}
              onClick={() => setCurrentTrack(track)}
            >
              <Typography variant="body2">{track.timestamp}</Typography>
              <Stack direction="row" spacing={1}>
                <Button
                  variant="text"
                  startIcon={<DownloadIcon />}
                  href={track.midiData}
                  download={`generated_${track.id}.mid`}
                  size="small"
                >
                  MIDI
                </Button>
                <Button
                  variant="text"
                  startIcon={<DownloadIcon />}
                  href={`http://localhost:8000/audio/${track.audioSrc}`}
                  download={`generated_${track.id}.wav`}
                  size="small"
                >
                  WAV
                </Button>
                <Button
                  variant="text"
                  startIcon={<DownloadIcon />}
                  href={`http://localhost:8000/audio/${track.audioSrc.replace('.wav', '.mp3')}`} // Assuming mp3 path is same but extension is .mp3
                  download={`generated_${track.id}.mp3`}
                  size="small"
                >
                  MP3
                </Button>
              </Stack>
            </Box>
          ))
        )}
      </Box>
    </Box>
  );
}

export default HistoryPanel;