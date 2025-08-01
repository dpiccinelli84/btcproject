

import json
import os
import numpy as np

def _transpose_sequence(sequence, semitones):
    """Transposes a MIDI note sequence by a given number of semitones."""
    transposed_sequence = []
    for note_val in sequence:
        transposed_note = note_val + semitones
        # Ensure notes stay within a reasonable MIDI range (e.g., 21-108 for piano, but guitar is narrower)
        # For now, we'll just transpose. If out of range, the model might learn to avoid them.
        transposed_sequence.append(transposed_note)
    return transposed_sequence

def _limit_consecutive_notes(sequence, max_consecutive=5):
    """Limits consecutive repetitions of the same note in a sequence."""
    if not sequence:
        return []

    filtered_sequence = []
    current_note = None
    consecutive_count = 0

    for note_val in sequence:
        if note_val == current_note:
            consecutive_count += 1
        else:
            current_note = note_val
            consecutive_count = 1

        if consecutive_count <= max_consecutive:
            filtered_sequence.append(note_val)
    return filtered_sequence

def preprocess_data(data_path, output_path, genre=None):
    """
    Reads JAMS files in a directory, extracts the MIDI note sequences,
    and saves them to a text file.
    If a genre is specified, only processes files containing that genre in their name.
    Applies data augmentation through transposition.
    """
    all_sequences = []
    for filename in os.listdir(data_path):
        if filename.endswith(".jams"):
            # Filter by genre if specified
            if genre and genre.lower() not in filename.lower():
                continue

            file_path = os.path.join(data_path, filename)
            with open(file_path, 'r') as f:
                jams_data = json.load(f)
            
            # Extract note sequences from the JAMS file
            for annotation in jams_data['annotations']:
                if annotation['namespace'] == 'note_midi':
                    sequence = []
                    for note_data in annotation['data']:
                        sequence.append(int(round(note_data['value'])))
                    
                    # Apply note limiting
                    filtered_sequence = _limit_consecutive_notes(sequence, max_consecutive=5)

                    if filtered_sequence: # Ensure sequence is not empty after filtering
                        all_sequences.append(filtered_sequence)
                        
                        # Data Augmentation: Transpose sequences
                        for semitones in range(-5, 6): # Transpose by -5 to +5 semitones
                            if semitones == 0: # Original sequence is already added
                                continue
                            transposed_seq = _transpose_sequence(filtered_sequence, semitones)
                            all_sequences.append(transposed_seq)

    # Save the sequences to a text file
    with open(output_path, 'w') as f:
        for sequence in all_sequences:
            f.write(' '.join(map(str, sequence)) + '\n')

if __name__ == '__main__':
    # Get the absolute path of the project's root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    data_path = os.path.join(project_root, "data")
    
    # Process data for each genre
    genres = ["Rock", "Jazz", "Funk", "BN", "SS"] # Add other genres as needed
    for genre_name in genres:
        output_file = f"processed_sequences_{genre_name.lower()}.txt"
        output_path = os.path.join(project_root, "data", output_file)
        print(f"Processing {genre_name} genre...")
        preprocess_data(data_path, output_path, genre=genre_name)
        print(f"Saved {genre_name} sequences to {output_path}")

    # Also process all data without genre filtering for a general model
    output_path_all = os.path.join(project_root, "data", "processed_sequences_all.txt")
    print("Processing all genres...")
    preprocess_data(data_path, output_path_all)
    print(f"Saved all sequences to {output_path_all}")


