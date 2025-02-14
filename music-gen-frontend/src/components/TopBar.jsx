// src/components/TopBar.jsx
import React from 'react';
import { Box, Typography, FormControlLabel, Switch } from '@mui/material';

/**
 * TopBar component for the application header, including title and theme toggle.
 *
 * @param {object} props - Component props.
 * @param {boolean} props.darkMode - Current dark mode state.
 * @param {function} props.toggleTheme - Function to toggle dark mode.
 */
function TopBar({ darkMode, toggleTheme }) {
  return (
    <Box
      sx={{
        px: 3,
        py: 2,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: darkMode ? '#121212' : '#ffffff',
        borderBottom: '1px solid',
        borderColor: darkMode ? '#444' : '#ccc',
      }}
    >
      <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '0.05em' }}>
        🎵 AI Music Generator
      </Typography>
      <FormControlLabel
        control={<Switch checked={darkMode} onChange={toggleTheme} color="secondary" />}
        label={darkMode ? 'Dark Mode' : 'Light Mode'}
      />
    </Box>
  );
}

export default TopBar;