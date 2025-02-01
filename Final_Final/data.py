''' this file includes the preprocessing steps to train the model'''
import os
import music21 as m21
import json

path = r"D:\test"
durations = [0.5,0.75,0.25,1,1.5,2,3,4]
timestep = 0.25
sequence_length = 128
single_path = 'single_song.txt'
import os
map_path = os.path.join(os.path.dirname(__file__), 'map.json')

'''load songfiles using music21'''
def loadfiles(path, max_limit=-1):
    songs = []
    for dirpath,subdir,files in os.walk(path):
      for file in files[:max_limit]:
        if file[-3:] == 'krn':
          song = m21.converter.parse(os.path.join(path,file))
          songs.append(song)
    return songs

'''filter the songs based on durations'''
def filter(songs,durations):
  
  for song in songs:
    for note in song.flatten().notesAndRests:
      if note.duration.quarterLength not in durations:
        songs.remove(song)
        break
  return songs
        
'''converting the into C/A keys, 24 keys->2''' 
def transpose(songs):
    tranposed_songs = []
    for song in songs:
      # get key from the song
      parts = song.getElementsByClass(m21.stream.Part)
      measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
      key = measures_part0[0][4]

      # estimate key using music21
      if not isinstance(key, m21.key.Key):
          key = song.analyze("key")

      # get interval for transposition. E.g., Bmaj -> Cmaj
      if key.mode == "major":
          interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
      elif key.mode == "minor":
          interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

      # transpose song by calculated interval
      tranposed_song = song.transpose(interval)
      tranposed_songs.append(tranposed_song)
    return tranposed_songs
  
'''encode the symbols for pitch and duration '''
def encoding(songs,timestep):
  single_song = ''
  for song in songs:
    encoded_song = []
    for event in song.flatten().notesAndRests:
      
      if isinstance(event,m21.note.Note):
        symbol = event.pitch.midi
      if isinstance(event,m21.note.Rest):
        symbol = 'R'
        
      steps = int(event.duration.quarterLength/timestep)
      for step in range(steps):
        if step==0:
          encoded_song.append(symbol)
        else:
          encoded_song.append('_')
          
    encoded_song = " ".join(map(str,encoded_song))
    single_song = single_song + encoded_song + " " + sequence_length * "\ "
  single_song = single_song[:-1]
  
  with open(single_path,'w') as f:
      f.write(single_song)
  return single_song
'''mapping for str to int'''
def mapping(single_song):
  dict_map = {}
  values = single_song.split()
  unique_values = set(values)
  for i , value in enumerate(unique_values):
    dict_map[value] = i
    
  with open(map_path,'w') as f:
    json.dump(dict_map,f,indent=4)
    
def training_samples(songs_path=single_path,sequence_length=sequence_length,map_path=map_path):
  
  with open(map_path,'r') as f:
    mapping = json.load(f)
  with open(songs_path,'r') as f:
    songs = f.read()
  # str to int mapping
  ls = songs.split()
  mapped_song = []
  for i in range(len(ls)):
    mapped_song.append(mapping[ls[i]])
  
  inputs = []
  targets = []
  for i in range(0,len(mapped_song)-sequence_length):
    inputs.append(mapped_song[i:i+sequence_length])
    targets.append(mapped_song[i+sequence_length])
  return inputs,targets

def get_vocabsize(map_path=map_path):
  with open(map_path,'r') as f:
    mapping = json.load(f)
  return len(mapping)

  
# songs = loadfiles(path, 15)
# print(f"len of songs {len(songs)}")
# songs = filter(songs,durations)
# print(f"len of songs {len(songs)}")
# songs = transpose(songs)
# song = encoding(songs,timestep)
# mapping(song)
  