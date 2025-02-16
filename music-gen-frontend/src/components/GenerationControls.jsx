import React from 'react';
import {
  Box,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Slider,
  Select,
  MenuItem,
  InputLabel,
  FormHelperText,
  Button,
  CircularProgress,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

/**
 * GenerationControls component for handling music generation parameters.
 *
 * @param {object} props - Component props.
 * @param {string} props.modelType - Currently selected model type ('Melody' or 'Drum').
 * @param {function} props.setModelType - Function to set the model type.
 * @param {string} props.seed - Seed melody for melody generation.
 * @param {function} props.setSeed - Function to set the seed melody.
 * @param {number} props.temperature - Temperature for generation creativity.
 * @param {function} props.setTemperature - Function to set the temperature.
 * @param {number} props.drumLength - Length of drum sequence for drum generation.
 * @param {function} props.setDrumLength - Function to set the drum sequence length.
 * @param {boolean} props.loading - Loading state during generation.
 * @param {string} props.error - Error message, if any.
 * @param {function} props.handleGenerate - Function to trigger music generation.
 * @param {object} props.seedOptions - Available seed melody options.
 * @param {boolean} props.darkMode - Current dark mode state for styling.
 */
function GenerationControls({
  modelType,
  setModelType,
  seed,
  setSeed,
  temperature,
  setTemperature,
  drumLength,
  setDrumLength,
  loading,
  error,
  handleGenerate,
  seedOptions,
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
      }}
    >
      <Typography variant="h6" gutterBottom>
        Generation Controls
      </Typography>
      <FormControl component="fieldset" sx={{ mb: 2 }}>
        <FormLabel component="legend">Select Model Type:</FormLabel>
        <RadioGroup row value={modelType} onChange={(e) => setModelType(e.target.value)}>
          <FormControlLabel value="Melody" control={<Radio />} label="Melody" />
          <FormControlLabel value="Drum" control={<Radio />} label="Drum" />
        </RadioGroup>
      </FormControl>
      <Box sx={{ mb: 2 }}>
        <Typography gutterBottom>Temperature (Creativity): {temperature}</Typography>
        <Slider
          value={temperature}
          onChange={(e, newValue) => setTemperature(newValue)}
          min={0.1}
          max={2.5}
          step={0.1}
          valueLabelDisplay="auto"
        />
      </Box>
      {modelType === 'Melody' && (
        <Box sx={{ mb: 2 }}>
          <FormControl fullWidth variant="outlined">
            <InputLabel id="seed-select-label">Seed Melody</InputLabel>
            <Select
              labelId="seed-select-label"
              value={seed}
              label="Seed Melody"
              onChange={(e) => setSeed(e.target.value)}
            >
              {Object.keys(seedOptions).map((key) => (
                <MenuItem key={key} value={seedOptions[key]}>
                  {`Seed ${key.replace('seed', '')}`}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>Select a seed melody</FormHelperText>
          </FormControl>
        </Box>
      )}
      {modelType === 'Drum' && (
        <Box sx={{ mb: 2 }}>
          <Typography gutterBottom>Drum Sequence Length: {drumLength}</Typography>
          <Slider
            value={drumLength}
            onChange={(e, newValue) => setDrumLength(newValue)}
            min={50}
            max={500}
            step={50}
            valueLabelDisplay="auto"
          />
        </Box>
      )}
      <Box sx={{ mt: 'auto', textAlign: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleGenerate}
          startIcon={<PlayArrowIcon />}
          sx={{
            animation: loading ? 'pulse 1s infinite' : 'none',
            '@keyframes pulse': {
              '0%': { transform: 'scale(1)' },
              '50%': { transform: 'scale(1.1)' },
              '100%': { transform: 'scale(1)' },
            },
          }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : 'Generate Music'}
        </Button>
        {error && (
          <Typography color="error" variant="body2" sx={{ mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

export default GenerationControls;