
import numpy as np
import json
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping # Import EarlyStopping

def load_sequences(file_path):
    """Loads sequences from a text file."""
    with open(file_path, 'r') as f:
        sequences = [list(map(int, line.strip().split())) for line in f.readlines()]
    return sequences

def create_model(vocab_size, embedding_dim, rnn_units, sequence_length):
    """Creates the RNN model."""
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=sequence_length-1),
        LSTM(rnn_units, return_sequences=True),
        Dropout(0.4),
        LSTM(int(rnn_units/2)),
        Dropout(0.4),
        Dense(vocab_size, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(genre=None, sequence_length=50, epochs=200): # Increased max epochs
    """Trains the model and saves it."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    if genre:
        data_file = f"processed_sequences_{genre.lower()}.txt"
        model_file = f"guitar_solo_generator_{genre.lower()}.h5"
        int_to_note_file = f"int_to_note_{genre.lower()}.json"
    else:
        data_file = "processed_sequences_all.txt"
        model_file = "guitar_solo_generator_all.h5"
        int_to_note_file = "int_to_note_all.json"

    data_path = os.path.join(project_root, "data", data_file)
    model_path = os.path.join(project_root, "models", model_file)
    int_to_note_path = os.path.join(project_root, "models", int_to_note_file)

    print(f"Loading sequences from {data_path}")
    sequences = load_sequences(data_path)
    
    # Create a vocabulary of unique notes
    notes = sorted(list(set(note for seq in sequences for note in seq)))
    note_to_int = {note: i for i, note in enumerate(notes)}
    vocab_size = len(notes)

    # Create input and output sequences
    input_sequences = []
    output_notes = []
    for seq in sequences:
        if len(seq) > sequence_length:
            for i in range(len(seq) - sequence_length):
                input_sequences.append([note_to_int[note] for note in seq[i:i+sequence_length-1]])
                output_notes.append(note_to_int[seq[i+sequence_length-1]])

    X = np.array(input_sequences)
    y = to_categorical(np.array(output_notes), num_classes=vocab_size)

    # Save the note-to-int mapping
    int_to_note = {i: n for i, n in enumerate(notes)}
    with open(int_to_note_path, 'w') as f:
        json.dump(int_to_note, f)

    model = create_model(vocab_size, 256, 1536, sequence_length)
    print(f"Training model for {genre if genre else 'all genres'}...")
    
    # Define EarlyStopping callback
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    model.fit(X, y, epochs=epochs, batch_size=64, validation_split=0.2, callbacks=[early_stopping])
    model.save(model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    genres = ["Rock", "Jazz", "Funk", "BN", "SS"]
    for genre_name in genres:
        train_model(genre=genre_name, epochs=200) # Max epochs for EarlyStopping
    
    # Train a model for all genres as well
    train_model(genre=None, epochs=200) # Max epochs for EarlyStopping
