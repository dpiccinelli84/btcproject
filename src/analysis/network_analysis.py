
import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from music21 import converter, note, chord

def midi_to_sequence(midi_path):
    """Converts a MIDI file to a sequence of MIDI note numbers."""
    midi = converter.parse(midi_path)
    sequence = []
    for element in midi.flat.notes:
        if isinstance(element, note.Note):
            sequence.append(element.pitch.midi)
        elif isinstance(element, chord.Chord):
            # For chords, we can take the root note or all notes
            # Here, we take the MIDI value of the first note in the chord
            sequence.append(element.pitches[0].midi)
    return sequence

def sequence_to_graph(sequence):
    """Builds a directed graph from a sequence of notes."""
    G = nx.DiGraph()
    if not sequence:
        return G
    
    # Add nodes for each unique note
    for note_val in set(sequence):
        G.add_node(note_val)
    
    # Add edges for sequential notes
    for i in range(len(sequence) - 1):
        u, v = sequence[i], sequence[i+1]
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1
        else:
            G.add_edge(u, v, weight=1)
    return G

def get_graph_metrics(G):
    """
    Calculates graph metrics. Handles disconnected graphs.
    """
    if not G.nodes():
        return {
            "avg_clustering": 0,
            "avg_path_length": 0,
            "num_nodes": 0,
            "num_edges": 0,
        }

    avg_clustering = nx.average_clustering(G)
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    # For path length, use the undirected version of the graph to avoid issues
    # with graphs that are not strongly connected.
    U = G.to_undirected()
    
    # Calculate the average shortest path length for each connected component
    # and then find the weighted average.
    connected_components = list(nx.connected_components(U))
    total_path_length = 0
    total_nodes = 0
    
    for component in connected_components:
        subgraph = U.subgraph(component)
        if subgraph.number_of_nodes() > 1:
            component_path_length = nx.average_shortest_path_length(subgraph)
            num_component_nodes = subgraph.number_of_nodes()
            total_path_length += component_path_length * num_component_nodes
            total_nodes += num_component_nodes

    if total_nodes > 0:
        avg_path_length = total_path_length / total_nodes
    else:
        avg_path_length = 0

    return {
        "avg_clustering": avg_clustering,
        "avg_path_length": avg_path_length,
        "num_nodes": num_nodes,
        "num_edges": num_edges,
    }

def compare_solos(generated_midi_path, original_jams_path):
    """Compares the network metrics of a generated solo and an original solo."""
    # Process the generated solo
    generated_sequence = midi_to_sequence(generated_midi_path)
    generated_graph = sequence_to_graph(generated_sequence)
    generated_metrics = get_graph_metrics(generated_graph)

    # Process the original solo from JAMS file
    with open(original_jams_path, 'r') as f:
        jams_data = json.load(f)
    
    original_sequence = []
    for annotation in jams_data['annotations']:
        if annotation['namespace'] == 'note_midi':
            for note_data in annotation['data']:
                original_sequence.append(int(round(note_data['value'])))
            break # Use the first available annotation

    original_graph = sequence_to_graph(original_sequence)
    original_metrics = get_graph_metrics(original_graph)

    # Print a comparison table
    print("| Metric                        | Generated Solo | Original Solo |")
    print("|-------------------------------|----------------|---------------|")
    for metric in generated_metrics:
        print(f"| {metric:<29} | {generated_metrics[metric]:<14} | {original_metrics.get(metric, 'N/A'):<13} |")

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    generated_midi_path = os.path.join(project_root, "output", "generated_solo.mid")
    
    # Find the first JAMS file in the data directory to use as a reference
    data_path = os.path.join(project_root, "data")
    original_jams_file = None
    for filename in os.listdir(data_path):
        if filename.endswith(".jams"):
            original_jams_file = os.path.join(data_path, filename)
            break
    
    if original_jams_file:
        compare_solos(generated_midi_path, original_jams_file)
    else:
        print("No JAMS files found in the data directory for comparison.")
