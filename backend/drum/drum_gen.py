import torch
import torch.nn as nn
import json
import numpy as np
from drum.drum_data import get_vocab_size

class Model(nn.Module):
  def __init__(self,in_size,vocab_size,hidden_dim,out_notes):
    super().__init__()
    self.lstm1 = nn.LSTM(input_size=in_size,hidden_size=hidden_dim,num_layers=1,batch_first=True)
    self.norm = nn.LayerNorm(hidden_dim)
    self.drop = nn.Dropout(0.1)
    
    self.mlp = nn.Sequential(
      nn.Linear(hidden_dim,hidden_dim),
      nn.Dropout(0.1),
      nn.Linear(hidden_dim,out_notes)
    )
    self.embedding = nn.Embedding(vocab_size,hidden_dim)
  def forward(self,x):
    x = self.embedding(x)
    _,(h,_) = self.lstm1(x)
    x = self.norm(h.squeeze(0))
    x = self.drop(x)
    x = self.mlp(h.squeeze(0))
    return x
  

class DrumGenerator:
    def __init__(self, model_path, map_path, sequence_length=128, hidden_dim=256):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.sequence_length = sequence_length
        self.hidden_dim = hidden_dim
        
        # Load vocabulary mapping
        with open(map_path, 'r') as f:
            self.mapping = json.load(f)
        self.reverse_mapping = {v: k for k, v in self.mapping.items()}
        self.vocab_size = len(self.mapping)
        
        # Initialize and load model
        self.model = Model(hidden_dim, self.vocab_size, hidden_dim, self.vocab_size).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device,weights_only=True))
        self.model.eval()

    def generate_sequence(self, seed_sequence=None, length=256, temperature=1.0):
        """
        Generate a drum sequence.
        Args:
            seed_sequence: Optional list of initial tokens. If None, will use random seed.
            length: Length of sequence to generate
            temperature: Controls randomness (higher = more random, lower = more deterministic)
        """
        if seed_sequence is None:
            # Generate random seed sequence
            seed_text = "38 _ _ _ 42 _ 42 _ 36 42 _ _ _ 42 _ _ _ 38 _ _ _ 42 _ 42 _ 36 _ 42"
            seed_sequence = [ self.mapping[i] for i in seed_text.split(" ")]
            # seed_sequence = np.random.choice(list(self.mapping.values()), 
                                        #   size=self.sequence_length)
            # print(seed_sequence); exit()
        # Convert to tensor and move to device
        current_sequence = torch.tensor(seed_sequence).unsqueeze(0).to(self.device)
        generated_sequence = list(seed_sequence)
        
        with torch.no_grad():
            for _ in range(length):
                # Get model prediction
                logits = self.model(current_sequence)
                
                # Apply temperature
                logits = logits / temperature
                
                # Sample from the distribution
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1).item()
                
                # Add to generated sequence
                generated_sequence.append(next_token)
                
                # Update current sequence
                current_sequence = torch.tensor(generated_sequence[-self.sequence_length:]).unsqueeze(0).to(self.device)
        
        return generated_sequence

    def decode_sequence(self, sequence):
        """Convert numeric sequence back to token sequence"""
        return [self.reverse_mapping[token] for token in sequence]

    def save_to_midi(self, sequence, output_path, timestep=0.1):
        """
        Convert generated sequence to MIDI file
        Args:
            sequence: List of tokens
            output_path: Path to save MIDI file
            timestep: Time between events in seconds
        """
        import pretty_midi
        
        pm = pretty_midi.PrettyMIDI()
        # For drums, we don't need a specific program number
        drums = pretty_midi.Instrument(program=0, is_drum=True)
        
        current_time = 0.0
        for token in sequence:
            if token in self.reverse_mapping:
                token_str = self.reverse_mapping[token]
                if token_str != '_':  # Skip silence tokens
                    # Create note (assuming 0.1 second duration for each hit)
                    note = pretty_midi.Note(
                        velocity=100,
                        pitch=int(token_str),
                        start=current_time,
                        end=current_time + 0.1
                    )
                    drums.notes.append(note)
            current_time += timestep
        
        pm.instruments.append(drums)
        pm.write(output_path)

# Example usage:
if __name__ == "__main__":
    # Initialize generator
    generator = DrumGenerator(
        model_path='model_drum.pth',
        map_path='drum_map.json'
    )
    
    # Generate sequence
    sequence = generator.generate_sequence(length=512, temperature=0.5)
    
    # Decode sequence
    decoded_sequence = generator.decode_sequence(sequence)
    
    # Save to MIDI
    generator.save_to_midi(sequence, 'generated_drums.mid')