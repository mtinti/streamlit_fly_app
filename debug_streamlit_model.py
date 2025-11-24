"""
Debug why Streamlit app predicts all peptides as Non-Flyers.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
from pathlib import Path
import numpy as np

# Add streamlit_app to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock streamlit for testing
class MockStreamlit:
    @staticmethod
    def cache_resource(func):
        return func

sys.modules['streamlit'] = MockStreamlit()

print("="*70)
print("DEBUG: STREAMLIT MODEL LOADING")
print("="*70)

# Import the actual load_model function from utils
from utils.prediction import load_model, encode_peptide, CLASSES_LABELS

# Load model using the Streamlit app's method
print("\n1. Loading model using Streamlit app's load_model()...")
try:
    model = load_model()
    print(f"   ✅ Model loaded: {type(model)}")
    print(f"   Model built: {model.built}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test predictions
print("\n2. Testing predictions...")
test_peptides = [
    "MVLSPADK",
    "LILTGAESK",
    "PEPTIDESEQ",
    "TNVKAAWGK",
]

print("\nPredictions:")
for seq in test_peptides:
    input_array = encode_peptide(seq)
    probs = model.predict(input_array, verbose=0)[0]
    predicted_idx = np.argmax(probs)
    predicted_class = CLASSES_LABELS[predicted_idx]

    print(f"\n{seq}:")
    print(f"  Probabilities: {probs}")
    print(f"  Predicted class: {predicted_class}")
    print(f"  Is Non-Flyer: {predicted_idx == 0}")

# Check model weights
print("\n" + "="*70)
print("3. Checking model weights...")
print("="*70)

# Check if weights are actually loaded
weights = model.get_weights()
print(f"Number of weight arrays: {len(weights)}")
print(f"Total parameters: {sum(w.size for w in weights)}")

# Check if weights look initialized (not all zeros)
first_layer_weights = weights[0] if weights else None
if first_layer_weights is not None:
    print(f"\nFirst layer weights shape: {first_layer_weights.shape}")
    print(f"First layer weights mean: {first_layer_weights.mean():.6f}")
    print(f"First layer weights std: {first_layer_weights.std():.6f}")
    print(f"First layer weights min: {first_layer_weights.min():.6f}")
    print(f"First layer weights max: {first_layer_weights.max():.6f}")

    # Check if all zeros (would indicate weights didn't load)
    if np.allclose(first_layer_weights, 0):
        print("   ⚠️  WARNING: Weights appear to be all zeros!")
    else:
        print("   ✅ Weights appear to be loaded (non-zero values)")

# Compare with expected results
print("\n" + "="*70)
print("4. Comparison with expected results")
print("="*70)

expected = {
    "MVLSPADK": "Strong Flyer",
    "LILTGAESK": "Strong Flyer",
    "PEPTIDESEQ": "Non-Flyer",
    "TNVKAAWGK": "Non-Flyer",
}

print("\nExpected vs Actual:")
all_correct = True
for seq in test_peptides:
    input_array = encode_peptide(seq)
    probs = model.predict(input_array, verbose=0)[0]
    predicted_idx = np.argmax(probs)
    predicted_class = CLASSES_LABELS[predicted_idx]
    expected_class = expected[seq]

    match = "✅" if predicted_class == expected_class else "❌"
    print(f"{match} {seq:15s}: Expected={expected_class:20s}, Got={predicted_class}")

    if predicted_class != expected_class:
        all_correct = False

print("\n" + "="*70)
if all_correct:
    print("✅ ALL PREDICTIONS CORRECT!")
else:
    print("❌ PREDICTIONS DON'T MATCH EXPECTED!")
    print("\nPossible issues:")
    print("  1. Weights not loaded correctly")
    print("  2. Model architecture doesn't match weights")
    print("  3. Model.build() called before weights loaded")
    print("  4. Wrong weights file being used")
print("="*70)
