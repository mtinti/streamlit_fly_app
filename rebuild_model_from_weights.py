"""
Rebuild model from weights file and save in portable format.

This script:
1. Reconstructs the model architecture using dlomix
2. Loads the weights from the training checkpoint
3. Re-saves the model in a portable format
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
print("REBUILDING MODEL FROM WEIGHTS")
print("="*70)

# Step 1: Import dlomix and create model architecture
print("\n1. Creating model architecture using dlomix...")
try:
    from dlomix.models import DetectabilityModel

    # Create model with same configuration as training
    # DetectabilityModel signature: __init__(self, num_units, num_classes=4, ...)
    num_units = 64  # Standard configuration from notebook
    num_classes = 4  # Non-Flyer, Weak, Intermediate, Strong Flyer
    seq_length = 40

    print(f"   Model configuration: num_units={num_units}, num_classes={num_classes}, seq_length={seq_length}")

    # Create model instance
    model = DetectabilityModel(num_units=num_units, num_classes=num_classes)

    # Build the model with correct input shape (batch_size, seq_length)
    model.build(input_shape=(None, seq_length))

    print("   ✅ Model architecture created!")
    print(f"   Model type: {type(model)}")

except Exception as e:
    print(f"   ❌ Error creating model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Load weights from checkpoint
print("\n2. Loading weights from checkpoint...")
weights_path = parent_dir / "notebooks" / "output" / "weights" / "new_base_model" / "base_model_weights_detectability" / "base_model_weights_detectability"

if not weights_path.parent.exists():
    print(f"   ❌ Weights directory not found: {weights_path.parent}")
    sys.exit(1)

try:
    model.load_weights(str(weights_path))
    print(f"   ✅ Weights loaded from: {weights_path}")
except Exception as e:
    print(f"   ❌ Error loading weights: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test the model works
print("\n3. Testing model predictions...")
dummy_input = tf.constant([[1, 2, 3, 4, 5] + [0] * 35], dtype=tf.int32)
try:
    output = model.predict(dummy_input, verbose=0)
    print(f"   ✅ Model prediction works! Output shape: {output.shape}")
    print(f"   Output probabilities: {output[0]}")
    print(f"   Sum of probabilities: {output[0].sum():.6f} (should be ~1.0)")
except Exception as e:
    print(f"   ❌ Model prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Re-save the model in portable format
print("\n4. Saving model in portable format...")
new_model_path = Path(__file__).parent / "models" / "detectability_model"

# Remove old model if exists
if new_model_path.exists():
    import shutil
    shutil.rmtree(new_model_path)
    print(f"   Removed old model at: {new_model_path}")

try:
    # Save without optimizer to reduce size
    model.save(
        str(new_model_path),
        save_format='tf',
        include_optimizer=False,
    )
    print(f"   ✅ Model saved to: {new_model_path}")
except Exception as e:
    print(f"   ❌ Error saving model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Verify the new model loads WITHOUT dlomix
print("\n5. Verifying new model loads without dlomix...")

# Remove dlomix from path
for path in list(sys.path):
    if 'dlomix' in path.lower() or str(parent_dir / "src") in path:
        try:
            sys.path.remove(path)
        except:
            pass

# Remove dlomix from loaded modules
modules_to_remove = [m for m in sys.modules.keys() if 'dlomix' in m.lower()]
for module in modules_to_remove:
    del sys.modules[module]

print("   Removed dlomix from environment")

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
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 6: Check model size
print("\n6. Checking model size...")
import subprocess
result = subprocess.run(['du', '-sh', str(new_model_path)], capture_output=True, text=True)
size = result.stdout.split()[0]
print(f"   Model size: {size}")

print("\n" + "="*70)
print("✅ MODEL REBUILT SUCCESSFULLY!")
print("="*70)
print("\nThe model has been rebuilt from weights and saved without dlomix dependencies.")
print("You can now use it in the Streamlit app.")
print("\nNext step: Test the Streamlit app:")
print("  streamlit run streamlit_app.py")
