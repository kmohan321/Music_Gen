import torch
import torch.nn as nn
from Final_Final.data import get_vocabsize
import json
import music21 as m21

device = 'cuda' if torch.cuda.is_available() else 'cpu'

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
  
hidden_dim = 256
vocab_size = get_vocabsize()
model = Model(hidden_dim,vocab_size,hidden_dim,vocab_size).to(device)

model.load_state_dict(torch.load("Final_Final/model.pth"))

def Malody_Generator(seed,num_steps,sequence_length,temperature):

    with open('Final_Final/map.json','r') as f:
      mapping = json.load(f)
      
    melody = seed.split()
    seed = '/ ' * sequence_length + seed
    mapping['/'] = 2
    seed = seed.split()
    int_seed = [ mapping[item] for item in seed]
    
    for i in range(num_steps):
        seed = int_seed[-sequence_length:]
        seed = torch.tensor(seed).to(device)
        seed = seed.view(1,sequence_length)
        model.eval()
        with torch.no_grad():
            prediction = model(seed)
        probabilities = torch.softmax(prediction / temperature, dim=-1)
        index = torch.multinomial(probabilities, num_samples=1).item()
        gen_note = [k for k, v in mapping.items() if v==index][0]
        
        if gen_note == "\\":
            break
        int_seed.append(index)
        melody.append(gen_note)
        
    return melody

def save_melody(melody, step_duration=0.25, format="midi", file_name="mel.mid"):
    """Converts a melody into a MIDI file

    :param melody (list of str):
    :param min_duration (float): Duration of each time step in quarter length
    :param file_name (str): Name of midi file
    :return:
    """

    # create a music21 stream
    stream = m21.stream.Stream()

    start_symbol = None
    step_counter = 1

    # parse all the symbols in the melody and create note/rest objects
    for i, symbol in enumerate(melody):

        # handle case in which we have a note/rest
        if symbol != "_" or i + 1 == len(melody):

            # ensure we're dealing with note/rest beyond the first one
            if start_symbol is not None:

                quarter_length_duration = step_duration * step_counter # 0.25 * 4 = 1

                # handle rest
                if start_symbol == "R":
                    m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                # handle note
                else:
                    m21_event = m21.note.Note(int(start_symbol), quarterLength=quarter_length_duration)

                stream.append(m21_event)

                # reset the step counter
                step_counter = 1

            start_symbol = symbol

        # handle case in which we have a prolongation sign "_"
        else:
            step_counter += 1

    # write the m21 stream to a midi file
    stream.write(format, file_name)

seed_dict ={
    'seed1':"_ 60 _ _ _ 55 _ _ _ 65 _",
    'seed2':"_ 67 _ 65 _ 64 _ 62 _ 60 _",
    'seed3':"_ 69 _ 65 _ 67 _ 69 _ 67 _ 65 _ 64 _",
    'seed4':"64 _ 69 _ _ _ 71 _ 72 _ _ 71",
    'seed5':"_ 67 _ 64 _ 60 _ _ R 76 _",
    'seed6':"71 _ _ 69 68 _ 69 _ _ _ _ _ R _ _ _",
    'seed7':"_ 62 _ _ _ R _ _ _ 55 _ _ _ 67 _ _ _ 67 _",
    'seed8':"_ 62 _ _ _ _ _ 60 _ 60 _ _ _ 55 _"
}

seed = "_ 67 _ 65 _ 64 _ 62 _ 60 _"
seed2 = "_ 60 _ _ _ 55 _ _ _ 65 _"
melody = Malody_Generator(seed2,200,128,1.7)
print(melody)
print(len(melody))
save_melody(melody) 