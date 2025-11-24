# Model Loading Issue - Diagnosis and Solution

## Problem Summary

The detectability model cannot be loaded from the SavedModel format, even with dlomix imported. The error indicates:

```
ValueError: Unable to restore custom object of class "GRU" (type _tf_keras_rnn_layer)
```

## Root Cause

The model was saved with layers that weren't properly built before serialization. This is evidenced by the warnings:

```
WARNING:tensorflow:Skipping full serialization of Keras layer <Masking>, because it is not built.
WARNING:tensorflow:Skipping full serialization of Keras layer <GRU>, because it is not built.
```

This is a known issue with Keras 2.15 and dlomix's DetectabilityModel architecture when using certain layer configurations.

## Attempted Solutions

1. ❌ Loading without dlomix → Failed (missing custom objects)
2. ❌ Loading with dlomix imported → Failed (GRU serialization issue)
3. ❌ Rebuilding from weights → Model saves but still can't load
4. ❌ Using `compile=False` → No effect

## Recommended Solutions

### Option 1: Re-export Model from Notebook (RECOMMENDED)

Add this cell to the end of your notebook to properly export the model:

```python
# Ensure model is built by running a dummy prediction first
import numpy as np
dummy_input = np.array([[1, 2, 3, 4, 5] + [0] * 35], dtype=np.int32)
_ = model.predict(dummy_input, verbose=0)

# Now save the model
output_path = 'output/saved_models/detectability_model_fixed'
model.save(
    output_path,
    save_format='tf',
    include_optimizer=False,  # Don't save optimizer to reduce size
)
print(f"Model saved to: {output_path}")

# Verify it loads correctly
test_model = tf.keras.models.load_model(output_path)
test_output = test_model.predict(dummy_input, verbose=0)
print(f"✅ Model loads and predicts correctly!")
print(f"Output shape: {test_output.shape}")
```

### Option 2: Use H5 Format Instead

Try saving in H5 format which sometimes handles custom layers better:

```python
# In notebook
model.save('output/saved_models/detectability_model.h5', save_format='h5')

# Then in Streamlit app
model = tf.keras.models.load_model('models/detectability_model.h5')
```

### Option 3: Save/Load Weights Only

If full model saving continues to fail, save just the weights and reconstruct:

**In notebook:**
```python
# Save weights
model.save_weights('output/weights/detectability_model_weights.h5')

# Save architecture as JSON
import json
with open('output/model_config.json', 'w') as f:
    json.dump({
        'num_units': 64,
        'num_classes': 4,
        'seq_length': 40
    }, f)
```

**In Streamlit app:**
```python
from dlomix.models import DetectabilityModel
import json

# Load config
with open('models/model_config.json', 'r') as f:
    config = json.load(f)

# Recreate model
model = DetectabilityModel(
    num_units=config['num_units'],
    num_classes=config['num_classes']
)
model.build(input_shape=(None, config['seq_length']))

# Load weights
model.load_weights('models/detectability_model_weights.h5')
```

### Option 4: Convert to TensorFlow.js Format

Export as TFJS which has better serialization:

```python
# In notebook
import tensorflowjs as tfjs
tfjs.converters.save_keras_model(model, 'output/tfjs_model')
```

Then use the TFJS model in a web app.

## Current Status

- ✅ Model architecture is correct
- ✅ Weights are available (`notebooks/output/weights/new_base_model/base_model_weights_detectability`)
- ✅ Model can be created and loaded with weights
- ❌ SavedModel format export is broken
- ❌ Model cannot be loaded standalone

## Next Steps

1. **Re-run the notebook** with Option 1 above to create a properly serialized model
2. Copy the new model to `streamlit_app/models/`
3. Test loading with:
   ```bash
   python verify_model.py
   ```
4. If successful, test the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Alternative: Deploy with dlomix

If model export continues to fail, you can:

1. Keep dlomix as a dependency (already added to `requirements.txt`)
2. Use the weights-only approach (Option 3 above)
3. Reconstruct the model at startup in the Streamlit app

This is less ideal but will work reliably.

## Technical Details

- **TensorFlow version**: 2.15.1
- **Keras version**: 2.15.0
- **DLOmix**: Using DetectabilityModel
- **Architecture**: Bidirectional GRU with encoder-decoder
- **Issue**: GRU layers not properly built before save

## References

- Keras SavedModel documentation: https://www.tensorflow.org/guide/keras/save_and_serialize
- DLOmix GitHub: https://github.com/wilhelm-lab/dlomix
- Related issues: Keras layer serialization with custom models
