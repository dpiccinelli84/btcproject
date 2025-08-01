import os
import json
import sys
from collections import defaultdict
import numpy as np # Import numpy for np.mean

# Add the project root to sys.path to allow absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Now perform absolute imports
from src.generation.generate import read_midi_file
from src.analysis.network_analyzer import analyze_midi_sequence_as_network
from src.data_preprocessing.data_preprocessing import _limit_consecutive_notes # Import the note limiting function

def analyze_original_data_metrics(data_path, genres):
    """
    Analyzes the original JAMS files to calculate average network metrics per genre.
    """
    print("\n--- Analyzing Original Data Metrics ---")
    genre_metrics = defaultdict(lambda: defaultdict(list))

    for genre_name in genres:
        print(f"Processing original {genre_name} data...")
        for filename in os.listdir(data_path):
            if filename.endswith(".jams") and genre_name.lower() in filename.lower():
                file_path = os.path.join(data_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        jams_data = json.load(f)
                    
                    sequence = []
                    for annotation in jams_data['annotations']:
                        if annotation['namespace'] == 'note_midi':
                            for note_data in annotation['data']:
                                sequence.append(int(round(note_data['value'])))
                    
                    # Apply the same note limiting as in preprocessing
                    filtered_sequence = _limit_consecutive_notes(sequence, max_consecutive=5)

                    if filtered_sequence:
                        metrics = analyze_midi_sequence_as_network(filtered_sequence)
                        for key, value in metrics.items():
                            genre_metrics[genre_name][key].append(value)

                except Exception as e:
                    print(f"Error processing original JAMS file {filename}: {e}")
    
    print("\n--- Average Original Data Metrics per Genre ---")
    for genre, metrics_list in genre_metrics.items():
        print(f"\nGenre: {genre}")
        for metric_name, values in metrics_list.items():
            if values:
                print(f"- {metric_name}: {np.mean(values):.4f}")
            else:
                print(f"- {metric_name}: N/A")
    print("------------------------------------------")

def evaluate_generated_solos(output_dir):
    """
    Evaluates generated solos by analyzing their network metrics.
    """
    print("\n--- Analyzing Generated Solos ---")
    generated_files = [f for f in os.listdir(output_dir) if f.endswith('.mid')]

    if not generated_files:
        print(f"No generated MIDI files found in {output_dir}. Please generate some solos first.")
        return

    for filename in generated_files:
        file_path = os.path.join(output_dir, filename)
        print(f"\nAnalyzing {filename}...")
        
        midi_notes = read_midi_file(file_path)
        if midi_notes:
            metrics = analyze_midi_sequence_as_network(midi_notes)
            for key, value in metrics.items():
                print(f"- {key}: {value}")
        else:
            print(f"Could not read notes from {filename}.")

    print("\n--- Objective Evaluation Complete ---")

if __name__ == '__main__':
    # Define paths
    output_dir = os.path.join(project_root, "output")
    original_data_dir = os.path.join(project_root, "data") # Original JAMS files are here
    genres = ["Rock", "Jazz", "Funk", "BN", "SS"]

    print("--- Starting Objective Evaluation ---")

    # Analyze original data first
    analyze_original_data_metrics(original_data_dir, genres)

    # Then analyze generated solos
    evaluate_generated_solos(output_dir)
