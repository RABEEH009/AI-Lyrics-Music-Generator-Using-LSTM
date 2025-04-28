import numpy as np
import pretty_midi
import pickle
from tensorflow.keras.models import load_model
import os

def generate_sample_melody(output_path, theme, mood, style):
    """
    Generate a melody using the trained LSTM model and save it as a MIDI file.
    
    Args:
        output_path (str): Path to save the generated melody MIDI file.
        theme (str): Song theme (e.g., 'love', 'adventure').
        mood (str): Song mood (e.g., 'happy', 'melancholic').
        style (str): Song style (e.g., 'pop', 'rock').
    """
    # Load preprocessed data and model
    with open("models/note_to_int.pkl", "rb") as f:
        note_to_int = pickle.load(f)
    
    int_to_note = {num: note for note, num in note_to_int.items()}
    num_classes = len(note_to_int)
    
    model = load_model("models/melody_model_fast.h5")
    sequence_length = 50  # Match preprocess.py
    
    # Adjust generation parameters based on theme, mood, style
    note_density = {'happy': 0.8, 'melancholic': 0.6, 'energetic': 1.0}.get(mood, 0.8)
    tempo = {'pop': 120, 'rock': 140, 'classical': 100}.get(style, 120)
    
    # Start with a random seed sequence
    X = np.load("models/X.npy")
    seed_idx = np.random.randint(0, len(X))
    pattern = X[seed_idx].copy()  # Shape: (sequence_length, 1)
    
    # Generate melody (e.g., 100 notes)
    prediction_output = []
    for _ in range(100):
        # Reshape for model input
        input_seq = pattern.reshape(1, sequence_length, 1)
        prediction = model.predict(input_seq, verbose=0)
        
        # Sample from prediction with mood-based temperature
        temperature = 1.0 / note_density
        prediction = np.log(prediction + 1e-6) / temperature
        exp_preds = np.exp(prediction)
        prediction = exp_preds / np.sum(exp_preds)
        
        predicted_int = np.random.choice(range(num_classes), p=prediction[0])
        prediction_output.append(predicted_int)
        
        # Update pattern
        new_note = np.array([[predicted_int / float(num_classes)]])
        pattern = np.vstack((pattern[1:], new_note))
    
    # Convert integers to MIDI notes
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano
    
    current_time = 0.0
    note_duration = 60.0 / tempo / 2  # Eighth notes at given tempo
    
    for note_int in prediction_output:
        note_name = int_to_note.get(note_int, '60')  # Default to C4
        pitch = int(note_name)
        note = pretty_midi.Note(
            velocity=100,
            pitch=pitch,
            start=current_time,
            end=current_time + note_duration
        )
        instrument.notes.append(note)
        current_time += note_duration
    
    midi.instruments.append(instrument)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save MIDI file
    midi.write(output_path)