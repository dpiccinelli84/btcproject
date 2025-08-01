import networkx as nx
import numpy as np

def analyze_midi_sequence_as_network(midi_sequence):
    """
    Analyzes a sequence of MIDI notes as a complex network.

    Nodes are unique MIDI notes.
    Directed edges represent transitions between consecutive notes.
    Edge weights represent the frequency of a transition.

    Args:
        midi_sequence (list): A list of MIDI note numbers.

    Returns:
        dict: A dictionary containing network metrics.
    """
    if not midi_sequence:
        return {
            "num_nodes": 0,
            "num_edges": 0,
            "avg_degree": 0,
            "clustering_coefficient": 0,
            "density": 0,
            "sequence_length": 0
        }

    G = nx.DiGraph() # Directed graph

    # Add nodes and edges
    for i in range(len(midi_sequence) - 1):
        current_note = midi_sequence[i]
        next_note = midi_sequence[i+1]

        # Add nodes (unique notes)
        G.add_node(current_note)
        G.add_node(next_note)

        # Add or update edge weight
        if G.has_edge(current_note, next_note):
            G[current_note][next_note]['weight'] += 1
        else:
            G.add_edge(current_note, next_note, weight=1)

    # Handle single note sequences (add the note as a node)
    if len(midi_sequence) == 1:
        G.add_node(midi_sequence[0])

    metrics = {}
    metrics["sequence_length"] = len(midi_sequence)
    metrics["num_nodes"] = G.number_of_nodes()
    metrics["num_edges"] = G.number_of_edges()

    if G.number_of_nodes() > 0:
        # Average degree (considering both in and out degrees for directed graph)
        degrees = [G.degree(node) for node in G.nodes()]
        metrics["avg_degree"] = np.mean(degrees) if degrees else 0

        # Clustering coefficient (for directed graphs, usually requires conversion to undirected or specific algorithms)
        # For simplicity, we'll use the undirected version for now, as it's a common metric.
        # The papers often discuss clustering coefficient in a general network context.
        metrics["clustering_coefficient"] = nx.average_clustering(G.to_undirected())

        # Density
        metrics["density"] = nx.density(G)
    else:
        metrics["avg_degree"] = 0
        metrics["clustering_coefficient"] = 0
        metrics["density"] = 0

    return metrics

if __name__ == '__main__':
    # Example usage with a sample MIDI sequence
    sample_midi_sequence = [60, 62, 64, 60, 65, 64, 62, 60, 60, 60, 62, 64, 65, 67, 65, 64, 62, 60]
    metrics = analyze_midi_sequence_as_network(sample_midi_sequence)
    print("Network Metrics for Sample Sequence:")
    for key, value in metrics.items():
        print(f"- {key}: {value}")

    # Example with a repetitive sequence (should have different metrics after preprocessing)
    repetitive_sequence = [60, 60, 60, 60, 60, 60, 60, 60, 62, 62, 62, 62, 64, 64, 64, 64]
    # This sequence would be preprocessed before analysis, but here we show raw
    metrics_rep = analyze_midi_sequence_as_network(repetitive_sequence)
    print("\nNetwork Metrics for Repetitive Sequence:")
    for key, value in metrics_rep.items():
        print(f"- {key}: {value}")
