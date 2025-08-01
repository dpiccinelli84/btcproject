import numpy as np
import json
import os
from tensorflow.keras.models import load_model
from midiutil import MIDIFile # Import MIDIFile
import mido # Import mido

def read_midi_file(midi_file_path):
    """Reads a MIDI file and returns a list of MIDI note numbers."""
    notes = []
    try:
        mid = mido.MidiFile(midi_file_path)
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append(msg.note)
    except Exception as e:
        print(f"Error reading MIDI file {midi_file_path}: {e}")
    return notes

def sample(preds, temperature=1.0):
    """Helper function to sample an index from a probability array."""
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def notes_to_midi(notes_str):
    """Converts a string of space-separated note names (e.g., 'C4 D#5') to a list of MIDI numbers."""
    midi_notes = []
    # Using a simple mapping for now, as music21 is removed
    # For a robust solution, a dedicated note parsing library or a manual lookup table would be needed.
    # Example: C4 -> 60, C#4 -> 61, D4 -> 62, etc.
    # This is a simplified placeholder. Real implementation would be more complex.
    note_map = {
        "C0": 12, "C#0": 13, "D0": 14, "D#0": 15, "E0": 16, "F0": 17, "F#0": 18, "G0": 19, "G#0": 20, "A0": 21, "A#0": 22, "B0": 23,
        "C1": 24, "C#1": 25, "D1": 26, "D#1": 27, "E1": 28, "F1": 29, "F#1": 30, "G1": 31, "G#1": 32, "A1": 33, "A#1": 34, "B1": 35,
        "C2": 36, "C#2": 37, "D2": 38, "D#2": 39, "E2": 40, "F2": 41, "F#2": 42, "G2": 43, "G#2": 44, "A2": 45, "A#2": 46, "B2": 47,
        "C3": 48, "C#3": 49, "D3": 50, "D#3": 51, "E3": 52, "F3": 53, "F#3": 54, "G3": 55, "G#3": 56, "A3": 57, "A#3": 58, "B3": 59,
        "C4": 60, "C#4": 61, "D4": 62, "D#4": 63, "E4": 64, "F4": 65, "F#4": 66, "G4": 67, "G#4": 68, "A4": 69, "A#4": 70, "B4": 71,
        "C5": 72, "C#5": 73, "D5": 74, "D#5": 75, "E5": 76, "F5": 77, "F#5": 78, "G5": 79, "G#5": 80, "A5": 81, "A#5": 82, "B5": 83,
        "C6": 84, "C#6": 85, "D6": 86, "D#6": 87, "E6": 88, "F6": 89, "F#6": 90, "G6": 91, "G#6": 92, "A6": 93, "A#6": 94, "B6": 95,
        "C7": 96, "C#7": 97, "D7": 98, "D#7": 99, "E7": 100, "F7": 101, "F#7": 102, "G7": 103, "G#7": 104, "A7": 105, "A#7": 106, "B7": 107,
        "C8": 108
    }
    for note_name in notes_str.split():
        midi_val = note_map.get(note_name.upper())
        if midi_val is not None:
            midi_notes.append(midi_val)
        else:
            print(f"Warning: Could not parse note '{note_name}'. Skipping.")
    return midi_notes

def generate_music(genre, seed_notes_str, output_path, sequence_length=50, generation_length=500, temperature=1.0):
    """Generates a new music sequence based on genre and seed notes, and saves it as a MIDI file."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    model_path = os.path.join(project_root, "models", f"guitar_solo_generator_{genre.lower()}.h5")
    int_to_note_path = os.path.join(project_root, "models", f"int_to_note_{genre.lower()}.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found for genre '{genre}': {model_path}")
    if not os.path.exists(int_to_note_path):
        raise FileNotFoundError(f"Note mapping not found for genre '{genre}': {int_to_note_path}")

    model = load_model(model_path)
    
    with open(int_to_note_path, 'r') as f:
        int_to_note = json.load(f)
    note_to_int = {int(note_val): int(index) for index, note_val in int_to_note.items()} # Ensure keys are int

    # DEBUGGING: Print int_to_note mapping
    print(f"int_to_note mapping for {genre}: {int_to_note}")

    # Convert seed notes string to MIDI numbers
    seed_midi_notes = notes_to_midi(seed_notes_str)
    if not seed_midi_notes:
        raise ValueError("No valid seed notes provided or parsed.")

    # Convert seed MIDI notes to vocabulary indices
    # Ensure all seed notes are in the model's vocabulary
    pattern = []
    for n_midi in seed_midi_notes:
        if n_midi in note_to_int:
            pattern.append(note_to_int[n_midi])
        else:
            print(f"Warning: Seed note MIDI {n_midi} not found in model vocabulary. Skipping.")
            # Optionally, handle this by mapping to a default note or raising an error
            # For now, we'll just skip it. If pattern becomes empty, it will raise an error later.

    if not pattern:
        raise ValueError("Seed notes could not be mapped to model vocabulary.")

    # Pad or truncate the pattern to sequence_length-1 if necessary
    if len(pattern) < sequence_length - 1:
        # Pad with a common note or a special 'start' token if available
        # For simplicity, let's just repeat the last note or pad with 0 if 0 is a valid note index
        # A more robust solution would involve a dedicated padding token or more sophisticated seed handling
        print(f"Warning: Seed sequence too short ({len(pattern)}). Padding with first note to {sequence_length-1}.")
        # Simple padding: repeat the first note
        if pattern:
            pattern = [pattern[0]] * (sequence_length - 1 - len(pattern)) + pattern
        else:
            # If pattern is empty after filtering, this means no valid seed notes.
            # This case should ideally be caught earlier.
            raise ValueError("Seed notes could not be mapped to model vocabulary and pattern is empty.")
    elif len(pattern) > sequence_length - 1:
        print(f"Warning: Seed sequence too long ({len(pattern)}). Truncating to {sequence_length-1}.")
        pattern = pattern[-(sequence_length - 1):] # Take the last part of the seed

    generated_sequence = []
    # Start generation from the seed pattern
    current_pattern = list(pattern) # Make a copy to modify

    for i in range(generation_length):
        prediction_input = np.reshape(current_pattern, (1, len(current_pattern)))
        prediction = model.predict(prediction_input, verbose=0)[0]
        
        # DEBUGGING: Print prediction probabilities and sampled index
        # print(f"--- Step {i+1} ---")
        # print(f"Prediction probabilities (top 5): {np.sort(prediction)[::-1][:5]}")
        # print(f"Indices of top 5: {np.argsort(prediction)[::-1][:5]}")
        # print(f"Temperature: {temperature}")

        index = sample(prediction, temperature)
        # print(f"Sampled index: {index}")
        
        result = int_to_note[str(index)] # Keys are strings from JSON
        generated_sequence.append(result)
        
        current_pattern.append(index)
        current_pattern = current_pattern[1:len(current_pattern)]

    # DEBUGGING: Print the first 20 notes of the generated sequence
    print(f"First 20 generated MIDI notes: {generated_sequence[:20]}")

    # Use midiutil to create the MIDI file
    midi_file = MIDIFile(1)  # One track
    track = 0
    time = 0
    channel = 0
    volume = 100  # 0-127
    tempo = 120  # BPM

    midi_file.addTrackName(track, time, "Generated Solo")
    midi_file.addTempo(track, time, tempo)

    for i, n_midi in enumerate(generated_sequence):
        # DEBUGGING: Print the MIDI value being added
        print(f"Adding MIDI note to file: {n_midi}")
        midi_file.addNote(track, channel, n_midi, time + i * 0.5, 0.5, volume) # Fixed duration of 0.5 beats

    with open(output_path, "wb") as f:
        midi_file.writeFile(f)

if __name__ == '__main__':
    # Example usage for testing
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Test with Rock genre and a specific seed
    try:
        generate_music(
            genre="Rock",
            seed_notes_str="C4 E4 G4",
            output_path=os.path.join(output_dir, "generated_rock_solo_seed.mid"),
            temperature=1.0
        )
        print("Generated rock solo with seed.")
    except Exception as e:
        print(f"Error generating rock solo: {e}")

    # Test with Jazz genre and a different seed
    try:
        generate_music(
            genre="Jazz",
            seed_notes_str="D5 F#5 A5 C6",
            output_path=os.path.join(output_dir, "generated_jazz_solo_seed.mid"),
            temperature=1.0
        )
        print("Generated jazz solo with seed.")
    except Exception as e:
        print(f"Error generating jazz solo: {e}")

    # Test with All genres and a simple seed
    try:
        generate_music(
            genre="All",
            seed_notes_str="C4",
            output_path=os.path.join(output_dir, "generated_all_solo_seed.mid"),
            temperature=1.0
        )
        print("Generated all genres solo with seed.")
    except Exception as e:
        print(f"Error generating all genres solo: {e}")
