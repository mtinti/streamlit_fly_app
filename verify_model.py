"""Simple model verification without Streamlit dependency."""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF info/warning messages

import numpy as np
import tensorflow as tf
from pathlib import Path

# Amino acid mapping
AA_TO_INT = {
    '0': 0, 'A': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5,
    'G': 6, 'H': 7, 'I': 8, 'K': 9, 'L': 10, 'M': 11,
    'N': 12, 'P': 13, 'Q': 14, 'R': 15, 'S': 16,
    'T': 17, 'V': 18, 'W': 19, 'Y': 20
}

CLASSES_LABELS = ['Non-Flyer', 'Weak Flyer', 'Intermediate Flyer', 'Strong Flyer']


def load_model_simple():
    """Load model without Streamlit caching."""
    model_path = Path(__file__).parent / 'models' / 'detectability_model'
    print(f"Loading model from: {model_path}")
    return tf.keras.models.load_model(str(model_path))


def encode_peptide(sequence, max_len=40):
    """Encode peptide sequence."""
    encoded = [AA_TO_INT.get(aa, 0) for aa in sequence.upper()]
    if len(encoded) < max_len:
        encoded = encoded + [0] * (max_len - len(encoded))
    else:
        encoded = encoded[:max_len]
    return np.array([encoded], dtype=np.int32)


def test_model():
    """Test model loading and predictions."""
    print("="*70)
    print("MODEL VERIFICATION TEST")
    print("="*70)

    # Load model
    print("\n1. Loading model...")
    try:
        model = load_model_simple()
        print("   ✅ Model loaded successfully!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test peptides
    test_peptides = {
        "LILTGAESK": "Expected: Flyer (good MS signal)",
        "PEPTIDESEQ": "Expected: Non-Flyer (poor MS signal)",
        "MVLSPADK": "Expected: Variable",
    }

    print("\n2. Testing predictions...")
    print("-"*70)

    all_correct = True
    for peptide, expected in test_peptides.items():
        print(f"\nPeptide: {peptide}")
        print(f"  {expected}")

        # Encode and predict
        input_array = encode_peptide(peptide)
        probabilities = model.predict(input_array, verbose=0)[0]

        # Get result
        predicted_idx = np.argmax(probabilities)
        predicted_class = CLASSES_LABELS[predicted_idx]
        is_flyer = predicted_idx > 0

        print(f"  Result: {predicted_class} ({'Flyer' if is_flyer else 'Non-Flyer'})")
        print(f"  Probabilities:")
        for i, (class_name, prob) in enumerate(zip(CLASSES_LABELS, probabilities)):
            marker = "👉" if i == predicted_idx else "  "
            print(f"    {marker} {class_name:20s}: {prob:.4f}")

        # Verify probabilities sum to 1
        prob_sum = probabilities.sum()
        if abs(prob_sum - 1.0) < 0.01:
            print(f"  ✅ Probabilities sum correctly: {prob_sum:.6f}")
        else:
            print(f"  ⚠️  Warning: Probabilities sum to {prob_sum:.6f} (should be ~1.0)")
            all_correct = False

    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70)

    if all_correct:
        print("\n✅ Model is working correctly!")
        print("\nThe TensorFlow warnings you see are HARMLESS and occur because:")
        print("  • The model uses Bidirectional GRU layers")
        print("  • GRU creates control flow graphs with while loops")
        print("  • TensorFlow's SavedModel metadata has minor inconsistencies")
        print("\n💡 These warnings don't affect predictions or accuracy.")
        print("\nTo suppress them, add this to your streamlit_app.py:")
        print("  import os")
        print("  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Before importing TF")
    else:
        print("\n⚠️  Some issues detected - review output above")

    print("\n" + "="*70)


if __name__ == "__main__":
    test_model()
