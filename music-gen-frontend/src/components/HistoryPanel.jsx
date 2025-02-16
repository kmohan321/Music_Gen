import React from 'react';
import { Box, Typography, Button, Stack } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

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
                    history.map((track) => {
                        const wavFilename = track.wavFilename;
                        const mp3Filename = track.mp3Filename;
                        return (
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
                                        href={`http://localhost:8000/audio/${track.wavFilename}`} // Full URL
                                        download={`generated_${track.id}.wav`}
                                        size="small"
                                    >
                                        WAV
                                    </Button>
                                    <Button
                                        variant="text"
                                        startIcon={<DownloadIcon />}
                                        href={`http://localhost:8000/audio/${track.mp3Filename}`} // Use mp3Filename
                                        download={`generated_${track.id}.mp3`}
                                        size="small"
                                    >
                                        MP3
                                    </Button>
                                </Stack>
                            </Box>
                        );
                    })
                )}
            </Box>
        </Box>
    );
}

export default HistoryPanel;