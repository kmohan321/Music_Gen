import os
from music21 import *
from collections import Counter
from tqdm.auto import tqdm
import torch
import numpy as np

filepath = r"D:\maestro-v3.0.0\tester"
all_midis= []
for i in tqdm(os.listdir(filepath)):
    if i.endswith(".mid"):
        tr = "/".join([filepath,i])
        midi = converter.parse(tr)
        all_midis.append(midi)
print(len(all_midis))

      
def extract_notes(file):
    notes = []
    pick = None
    for j in file:
        songs = instrument.partitionByInstrument(j)
        for part in songs.parts:
            pick = part.recurse()
            for element in pick:
                if isinstance(element, note.Note):
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append(".".join(str(n) for n in element.normalOrder))

    return notes

Corpus= extract_notes(all_midis)
print("Total notes in all the midis in the dataset:", len(Corpus))

def chords_n_notes(Snippet):
    Melody = []
    offset = 0 #Incremental
    for i in Snippet:
        #If it is chord
        if ("." in i or i.isdigit()):
            chord_notes = i.split(".") #Seperating the notes in chord
            notes = [] 
            for j in chord_notes:
                inst_note=int(j)
                note_snip = note.Note(inst_note)            
                notes.append(note_snip)
                chord_snip = chord.Chord(notes)
                chord_snip.offset = offset
                Melody.append(chord_snip)
        # pattern is a note
        else: 
            note_snip = note.Note(i)
            note_snip.offset = offset
            Melody.append(note_snip)
        # increase offset each iteration so that notes do not stack
        offset += 1
    Melody_midi = stream.Stream(Melody)   
    return Melody_midi

Melody_Snippet = chords_n_notes(Corpus[:100])
Melody_Snippet.write('midi','Melody_Generated.mid')


count_num = Counter(Corpus)
print("Total unique notes in the Corpus:", len(count_num))

import matplotlib.pyplot as plt
l1 = list(count_num.values())
# plt.figure(figsize=(18,3),facecolor="#97BACB")
# bins = np.arange(0,(max(l1)), 50) 
# plt.hist(l1, bins=bins, color="#97BACB")
# plt.axvline(x=100,color="#DBACC1")
# plt.title("Frequency Distribution Of Notes In The Corpus")
# plt.xlabel("Frequency Of Chords in Corpus")
# plt.ylabel("Number Of Chords")
# plt.show()

l1 = list(count_num.values())
print(min(l1))
print(max(l1))
print(sum(l1)/len(l1))
#cleaning the corpus 
rare_note =[]
for keys,value in count_num.items():
    if value < 100:
        rare_note.append(keys)
print(len(rare_note))        
        
for item in Corpus:
    if item in rare_note:
        Corpus.remove(item)


print('new length of corpus ',len(Corpus))

# Storing all the unique characters present in my corpus to bult a mapping dic. 
symb = sorted(list(set(Corpus)))

L_corpus = len(Corpus) #length of corpus
L_symb = len(symb) #length of total unique characters

#Building dictionary to access the vocabulary from indices and vice versa
mapping = dict((c, i) for i, c in enumerate(symb))
reverse_mapping = dict((i, c) for i, c in enumerate(symb))

print("Total number of characters:", L_corpus)
print("Number of unique characters:", L_symb)


length = 40
features_ = []
targets = []
for i in range(0, L_corpus - length, 1):
    feature = Corpus[i:i + length]
    target = Corpus[i + length]
    features_.append([mapping[j] for j in feature])
    targets.append(mapping[target])
    
    
L_datapoints = len(targets)
print("Total number of sequences in the Corpus:", L_datapoints)
print(features_[0])

torch.save(torch.Tensor(features_),'features.pth')
torch.save(torch.Tensor(targets),'targets.pth')


import numpy as np
from music21 import *
import torch.nn as nn
import torch

class Model(nn.Module):
  def __init__(self,in_size,hidden_dim,out_notes):
    super().__init__()
    self.lstm1 = nn.LSTM(input_size=in_size,hidden_size=hidden_dim,num_layers=1,batch_first=True)
    self.norm = nn.LayerNorm(hidden_dim)
    self.drop = nn.Dropout(0.1)
    self.lstm2 = nn.LSTM(input_size=hidden_dim,hidden_size=hidden_dim,num_layers=1,batch_first=True)
    
    self.mlp = nn.Sequential(
      nn.Linear(hidden_dim,hidden_dim),
      nn.Dropout(0.1),
      nn.Linear(hidden_dim,out_notes)
    )
  def forward(self,input):
    x,_ = self.lstm1(input)
    x = self.norm(x)
    x = self.drop(x)
    x,_ = self.lstm2(x)
    x = self.mlp(x[:,-1,:])
    return x


model = Model(1,256,263)
model.load_state_dict(torch.load('model.pth'))

def Malody_Generator(Note_Count,X_seed):
    seed = X_seed[np.random.randint(0,len(X_seed)-1)]
    seed = np.array(seed)
    Music = ""
    Notes_Generated=[]
    for i in range(Note_Count):
        seed = seed.reshape(1,length,1)
        seed = torch.Tensor(seed)
        model.eval()
        with torch.no_grad():
            prediction = model(seed)[0]
        index = torch.argmax(torch.softmax(prediction/1,dim=-1),dim=-1)
        # prediction = np.log(prediction) / 1.0 
        # exp_preds = np.exp(prediction)
        # print(exp_preds)
        # prediction = exp_preds / np.sum(exp_preds)
        # index = np.argmax(prediction)
        # index_N = index/ float(L_symb)   
        Notes_Generated.append(index.item())
        Music = [reverse_mapping[char] for char in Notes_Generated]
        seed = np.insert(seed[0],len(seed[0]),index)
        seed = seed[1:]
    #Now, we have music in form or a list of chords and notes and we want to be a midi file.
    Melody = chords_n_notes(Music)
    Melody_midi = stream.Stream(Melody)   
    return Music,Melody_midi


#getting the Notes and Melody created by the model
Music_notes, Melody = Malody_Generator(100,features_)
Melody.write('midi','Melody_Generated_trained.mid')
# Melody.show()