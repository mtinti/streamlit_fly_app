"""Model loading and prediction utilities."""

import numpy as np
import tensorflow as tf
import streamlit as st
from pathlib import Path


# Amino acid to integer mapping (matching the training configuration)
AA_TO_INT = {
    '0': 0, 'A': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5,
    'G': 6, 'H': 7, 'I': 8, 'K': 9, 'L': 10, 'M': 11,
    'N': 12, 'P': 13, 'Q': 14, 'R': 15, 'S': 16,
    'T': 17, 'V': 18, 'W': 19, 'Y': 20
}

# Class labels
CLASSES_LABELS = ['Non-Flyer', 'Weak Flyer', 'Intermediate Flyer', 'Strong Flyer']


@st.cache_resource
def load_model():
    """
    Load the detectability model and cache it.

    Uses Streamlit's cache_resource to load the model only once
    and reuse it across sessions.

    This function creates the model architecture and loads weights separately,
    avoiding SavedModel serialization issues.

    Returns
    -------
    tf.keras.Model
        Loaded TensorFlow model

    Raises
    ------
    FileNotFoundError
        If model weights are not found
    """
    # Path to model weights (not SavedModel format)
    weights_path = Path(__file__).parent.parent / 'notebooks' / 'output' / 'weights' / 'new_base_model' / 'base_model_weights_detectability' / 'base_model_weights_detectability'

    if not weights_path.parent.exists():
        raise FileNotFoundError(
            f"Model weights not found at {weights_path}. "
            "Please ensure the weights file exists in the notebooks output directory."
        )

    try:
        # Import dlomix to create model architecture
        from dlomix.models import DetectabilityModel

        # Model configuration (must match training configuration)
        num_units = 64
        num_classes = 4  # Non-Flyer, Weak, Intermediate, Strong Flyer

        # Create model architecture
        model = DetectabilityModel(num_units=num_units, num_classes=num_classes)

        # Build model with correct input shape
        model.build(input_shape=(None, 40))  # 40 is max_seq_length

        # Load weights from checkpoint
        model.load_weights(str(weights_path))

        return model
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}")


def encode_peptide(peptide_sequence, max_len=40):
    """
    Encode a peptide sequence into integer representation.

    Parameters
    ----------
    peptide_sequence : str
        Peptide sequence to encode
    max_len : int
        Maximum sequence length for padding (default: 40)

    Returns
    -------
    np.ndarray
        Encoded and padded sequence with shape (1, max_len)
    """
    # Convert to uppercase
    sequence = peptide_sequence.upper()

    # Encode: convert each amino acid to its integer representation
    encoded = [AA_TO_INT.get(aa, 0) for aa in sequence]

    # Pad or truncate to max_len
    if len(encoded) < max_len:
        encoded = encoded + [0] * (max_len - len(encoded))  # Pad with zeros
    else:
        encoded = encoded[:max_len]  # Truncate if too long

    # Convert to numpy array with batch dimension
    return np.array([encoded], dtype=np.int32)


def predict_peptide(peptide_sequence, model, max_len=40):
    """
    Predict detectability class for a single peptide sequence.

    Parameters
    ----------
    peptide_sequence : str
        A peptide sequence string (e.g., "PEPTIDESEQ")
    model : tf.keras.Model
        The trained DetectabilityModel
    max_len : int
        Maximum sequence length for padding (default: 40)

    Returns
    -------
    dict
        Dictionary containing predicted class, probabilities, and metadata
        Keys: 'sequence', 'predicted_class', 'predicted_class_index',
              'probabilities', 'is_flyer'
    """
    # Encode the sequence
    input_array = encode_peptide(peptide_sequence, max_len)

    # Make prediction
    probabilities = model.predict(input_array, verbose=0)[0]

    # Get predicted class
    predicted_class_idx = np.argmax(probabilities)
    predicted_class = CLASSES_LABELS[predicted_class_idx]

    # Create result dictionary
    result = {
        "sequence": peptide_sequence,
        "predicted_class": predicted_class,
        "predicted_class_index": int(predicted_class_idx),
        "probabilities": {
            CLASSES_LABELS[i]: float(prob)
            for i, prob in enumerate(probabilities)
        },
        "is_flyer": predicted_class_idx > 0  # Non-Flyer is class 0
    }

    return result


def predict_batch(peptides, model, max_len=40, batch_size=32):
    """
    Predict detectability for multiple peptides efficiently.

    Parameters
    ----------
    peptides : list of dict
        List of peptide dictionaries with 'sequence', 'start', 'end' keys
    model : tf.keras.Model
        The trained DetectabilityModel
    max_len : int
        Maximum sequence length for padding (default: 40)
    batch_size : int
        Batch size for prediction (default: 32)

    Returns
    -------
    list of dict
        List of prediction dictionaries with added prediction fields
    """
    if not peptides:
        return []

    # Encode all sequences
    sequences = [p['sequence'] for p in peptides]
    encoded_sequences = np.vstack([
        encode_peptide(seq, max_len) for seq in sequences
    ])

    # Batch prediction
    all_probabilities = model.predict(
        encoded_sequences,
        batch_size=batch_size,
        verbose=0
    )

    # Process results
    results = []
    for i, peptide in enumerate(peptides):
        probabilities = all_probabilities[i]
        predicted_class_idx = np.argmax(probabilities)
        predicted_class = CLASSES_LABELS[predicted_class_idx]

        result = {
            **peptide,  # Include original peptide info (sequence, start, end)
            'predicted_class': predicted_class,
            'predicted_class_index': int(predicted_class_idx),
            'probabilities': {
                CLASSES_LABELS[j]: float(prob)
                for j, prob in enumerate(probabilities)
            },
            'is_flyer': predicted_class_idx > 0
        }
        results.append(result)

    return results


def get_model_info():
    """
    Get information about the model.

    Returns
    -------
    dict
        Dictionary with model metadata
    """
    return {
        'name': 'Peptide Detectability Predictor',
        'version': '1.0',
        'description': 'Predicts whether peptides are detectable by mass spectrometry',
        'classes': CLASSES_LABELS,
        'input_length': 40,
        'framework': 'TensorFlow',
        'architecture': 'Bidirectional GRU with Attention',
    }
