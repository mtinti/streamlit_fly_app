"""
Fix model export to remove dlomix dependencies.

This script loads the model with dlomix available, then re-saves it
in a portable format without dlomix dependencies.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to access dlomix
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / "src"))

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np

print("="*70)
print("FIXING MODEL EXPORT")
print("="*70)

# Step 1: Load the original model with dlomix
print("\n1. Loading original model from notebook output...")
original_model_path = parent_dir / "notebooks" / "output" / "saved_models" / "detectability_model"

if not original_model_path.exists():
    print(f"❌ Original model not found at: {original_model_path}")
    print("\nPlease run the notebook cell that saves the model first.")
    sys.exit(1)

try:
    # Import dlomix to make custom objects available
    import dlomix
    from dlomix.models import DetectabilityModel

    model = tf.keras.models.load_model(str(original_model_path))
    print("   ✅ Original model loaded successfully!")
except Exception as e:
    print(f"   ❌ Error loading original model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test the model works
print("\n2. Testing model...")
dummy_input = tf.constant([[1, 2, 3, 4, 5] + [0] * 35], dtype=tf.int32)
try:
    output = model.predict(dummy_input, verbose=0)
    print(f"   ✅ Model prediction works! Output shape: {output.shape}")
except Exception as e:
    print(f"   ❌ Model prediction failed: {e}")
    sys.exit(1)

# Step 3: Re-save the model in a portable format
print("\n3. Re-saving model in portable format...")
new_model_path = Path(__file__).parent / "models" / "detectability_model"

# Remove old model if exists
if new_model_path.exists():
    import shutil
    shutil.rmtree(new_model_path)
    print(f"   Removed old model at: {new_model_path}")

try:
    # Save with options that make it more portable
    model.save(
        str(new_model_path),
        save_format='tf',
        include_optimizer=False,  # Don't save optimizer
    )
    print(f"   ✅ Model saved to: {new_model_path}")
except Exception as e:
    print(f"   ❌ Error saving model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Verify the new model loads WITHOUT dlomix
print("\n4. Verifying new model loads without dlomix...")

# Remove dlomix from path to simulate streamlit environment
for path in list(sys.path):
    if 'dlomix' in path.lower():
        sys.path.remove(path)

# Remove dlomix from loaded modules
modules_to_remove = [m for m in sys.modules.keys() if 'dlomix' in m.lower()]
for module in modules_to_remove:
    del sys.modules[module]

try:
    # Try to load WITHOUT dlomix
    test_model = tf.keras.models.load_model(str(new_model_path))
    print("   ✅ Model loads without dlomix!")

    # Test prediction
    test_output = test_model.predict(dummy_input, verbose=0)
    print(f"   ✅ Prediction works! Output shape: {test_output.shape}")

    # Verify outputs match
    diff = np.abs(output - test_output).max()
    print(f"   Max difference from original: {diff:.10f}")

    if diff < 1e-6:
        print("   ✅ Models produce identical outputs!")
    else:
        print(f"   ⚠️  Warning: Outputs differ by {diff}")

except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n   The model still has dlomix dependencies.")
    print("   This might be unavoidable with the current model architecture.")
    print("\n   SOLUTION: Update utils/prediction.py to use custom_objects")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Check model size
print("\n5. Checking model size...")
import subprocess
result = subprocess.run(['du', '-sh', str(new_model_path)], capture_output=True, text=True)
size = result.stdout.split()[0]
print(f"   Model size: {size}")

print("\n" + "="*70)
print("✅ MODEL EXPORT FIXED!")
print("="*70)
print("\nThe model has been re-saved without dlomix dependencies.")
print("You can now use it in the Streamlit app.")
print("\nNext step: Test the Streamlit app:")
print("  streamlit run streamlit_app.py")
