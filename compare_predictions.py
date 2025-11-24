"""
Compare predictions between notebook approach and Streamlit app approach.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
from pathlib import Path
import numpy as np

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

import tensorflow as tf
from dlomix.models import DetectabilityModel

print("="*70)
print("COMPARING PREDICTIONS: NOTEBOOK vs STREAMLIT APP")
print("="*70)

# Test peptides
test_sequences = [
    "MVLSPADK",
    "LILTGAESK",
    "PEPTIDESEQ",
    "TNVKAAWGK",
]

# Amino acid encoding
AA_TO_INT = {
    '0': 0, 'A': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5,
    'G': 6, 'H': 7, 'I': 8, 'K': 9, 'L': 10, 'M': 11,
    'N': 12, 'P': 13, 'Q': 14, 'R': 15, 'S': 16,
    'T': 17, 'V': 18, 'W': 19, 'Y': 20
}

def encode_peptide(sequence, max_len=40):
    """Encode peptide sequence."""
    encoded = [AA_TO_INT.get(aa, 0) for aa in sequence.upper()]
    if len(encoded) < max_len:
        encoded = encoded + [0] * (max_len - len(encoded))
    else:
        encoded = encoded[:max_len]
    return np.array([encoded], dtype=np.int32)

# Weights path
weights_path = Path(__file__).parent.parent / 'notebooks' / 'output' / 'weights' / 'new_base_model' / 'base_model_weights_detectability' / 'base_model_weights_detectability'

print(f"\nWeights path: {weights_path}")
print(f"Weights exist: {weights_path.parent.exists()}")

# ============================================================================
# METHOD 1: Notebook approach (exactly as in prediction notebook)
# ============================================================================
print("\n" + "="*70)
print("METHOD 1: NOTEBOOK APPROACH")
print("="*70)

try:
    # Check if there's a typo in the parameter name
    import inspect
    sig = inspect.signature(DetectabilityModel.__init__)
    params = list(sig.parameters.keys())
    print(f"DetectabilityModel parameters: {params}")

    # Try the notebook's approach - check for typo
    total_num_classes = 4
    num_cells = 64

    # Try both parameter names to see which works
    try:
        model1 = DetectabilityModel(num_units=num_cells, num_clases=total_num_classes)
        print("✅ Created model with 'num_clases' (notebook typo)")
        param_name = "num_clases"
    except TypeError as e:
        print(f"   'num_clases' failed: {e}")
        try:
            model1 = DetectabilityModel(num_units=num_cells, num_classes=total_num_classes)
            print("✅ Created model with 'num_classes' (correct spelling)")
            param_name = "num_classes"
        except TypeError as e2:
            print(f"   'num_classes' also failed: {e2}")
            # Try with just num_units
            model1 = DetectabilityModel(num_units=num_cells)
            print("✅ Created model with only 'num_units'")
            param_name = "num_units_only"

    model1.load_weights(str(weights_path))
    print("✅ Weights loaded (notebook approach)")

    # Test predictions
    print("\nPredictions (notebook approach):")
    for seq in test_sequences:
        input_array = encode_peptide(seq)
        pred = model1.predict(input_array, verbose=0)[0]
        print(f"  {seq:15s} -> {pred}")

except Exception as e:
    print(f"❌ Notebook approach failed: {e}")
    import traceback
    traceback.print_exc()
    model1 = None

# ============================================================================
# METHOD 2: Streamlit app approach (with build)
# ============================================================================
print("\n" + "="*70)
print("METHOD 2: STREAMLIT APP APPROACH (with build)")
print("="*70)

try:
    model2 = DetectabilityModel(num_units=64, num_classes=4)
    model2.build(input_shape=(None, 40))
    model2.load_weights(str(weights_path))
    print("✅ Model created with build() call")

    # Test predictions
    print("\nPredictions (streamlit approach):")
    for seq in test_sequences:
        input_array = encode_peptide(seq)
        pred = model2.predict(input_array, verbose=0)[0]
        print(f"  {seq:15s} -> {pred}")

except Exception as e:
    print(f"❌ Streamlit approach failed: {e}")
    import traceback
    traceback.print_exc()
    model2 = None

# ============================================================================
# METHOD 3: No build, just load weights
# ============================================================================
print("\n" + "="*70)
print("METHOD 3: NO BUILD CALL (like notebook)")
print("="*70)

try:
    model3 = DetectabilityModel(num_units=64, num_classes=4)
    # NO build() call
    model3.load_weights(str(weights_path))
    print("✅ Model created WITHOUT build() call")

    # Test predictions
    print("\nPredictions (no build):")
    for seq in test_sequences:
        input_array = encode_peptide(seq)
        pred = model3.predict(input_array, verbose=0)[0]
        print(f"  {seq:15s} -> {pred}")

except Exception as e:
    print(f"❌ No-build approach failed: {e}")
    import traceback
    traceback.print_exc()
    model3 = None

# ============================================================================
# COMPARE RESULTS
# ============================================================================
print("\n" + "="*70)
print("COMPARISON")
print("="*70)

if model1 and model2:
    print("\nComparing Method 1 (notebook) vs Method 2 (streamlit with build):")
    max_diff = 0
    for seq in test_sequences:
        input_array = encode_peptide(seq)
        pred1 = model1.predict(input_array, verbose=0)[0]
        pred2 = model2.predict(input_array, verbose=0)[0]
        diff = np.abs(pred1 - pred2).max()
        max_diff = max(max_diff, diff)
        print(f"  {seq:15s}: max_diff = {diff:.10f}")

    if max_diff < 1e-6:
        print(f"\n✅ Results are IDENTICAL (max diff: {max_diff:.10f})")
    else:
        print(f"\n⚠️  Results DIFFER (max diff: {max_diff:.10f})")

if model1 and model3:
    print("\nComparing Method 1 (notebook) vs Method 3 (no build):")
    max_diff = 0
    for seq in test_sequences:
        input_array = encode_peptide(seq)
        pred1 = model1.predict(input_array, verbose=0)[0]
        pred3 = model3.predict(input_array, verbose=0)[0]
        diff = np.abs(pred1 - pred3).max()
        max_diff = max(max_diff, diff)
        print(f"  {seq:15s}: max_diff = {diff:.10f}")

    if max_diff < 1e-6:
        print(f"\n✅ Results are IDENTICAL (max diff: {max_diff:.10f})")
    else:
        print(f"\n⚠️  Results DIFFER (max diff: {max_diff:.10f})")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("If results differ, we need to match the notebook approach exactly.")
print("Check the parameter names and whether build() should be called.")
