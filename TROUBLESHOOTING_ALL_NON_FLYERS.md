# Troubleshooting: All Peptides Showing as Non-Flyers

## Issue

You're seeing all peptides predicted as Non-Flyers in the Streamlit app, but the same model works correctly in tests and notebooks.

## Tests Show Everything Works

✅ Direct model loading test: PASS (correct predictions)
✅ Full workflow test: PASS (7 flyers, 1 non-flyer for hemoglobin)
✅ Batch prediction test: PASS
✅ Encoding test: PASS

**This means the code is correct, but something is wrong in the Streamlit runtime environment.**

## Immediate Solutions

### 1. Clear Streamlit Cache (Most Likely Fix)

Streamlit might be caching an old broken model. Clear it:

**Option A: In the app**
- Press `C` in the terminal where Streamlit is running
- Or click the menu (☰) → "Clear cache"

**Option B: Command line**
```bash
# Stop the app (Ctrl+C)
rm -rf ~/.streamlit/cache
streamlit run streamlit_app.py
```

### 2. Check You Have the Latest Code

Make sure you have the updated `utils/prediction.py`:

```bash
cd streamlit_app
grep -A5 "def load_model" utils/prediction.py
```

Should show:
```python
def load_model():
    # Path to model weights (not SavedModel format)
    weights_path = Path(__file__).parent.parent.parent / 'notebooks' ...
```

### 3. Verify Weights File Exists

```bash
ls -lh ../notebooks/output/weights/new_base_model/base_model_weights_detectability*
```

Should show two files (~1.4M total).

### 4. Check Debug Output

I added debug output to the app. Run it and look for:
```
DEBUG: Generated X predictions
DEBUG: First prediction: {...}
DEBUG: Flyer count: X
```

**If Flyer count is 0, there's a problem with the model.**
**If Flyer count > 0, the problem is with display/filtering.**

### 5. Test Outside Streamlit

Confirm the model works:
```bash
cd streamlit_app
python test_full_workflow.py
```

This should show 7 flyers for hemoglobin. If it doesn't, there's an environment issue.

## Common Causes

### Cause 1: Cached Old Model

**Symptom**: Model was loaded before the fix
**Fix**: Clear cache (Solution #1 above)

### Cause 2: Wrong Weights File

**Symptom**: Using fine-tuned instead of base model weights
**Check**:
```python
# In utils/prediction.py, should be:
weights_path = ... / 'new_base_model' / 'base_model_weights_detectability'
# NOT:
# 'new_fine_tuned_model' / 'fine_tuned_model_weights_detectability'
```

### Cause 3: Model Build Issue

**Symptom**: Model.build() called with wrong shape
**Fix**: Update utils/prediction.py to remove .build() call:

```python
# Remove this line:
# model.build(input_shape=(None, 40))

# Just use:
model = DetectabilityModel(num_units=64, num_classes=4)
model.load_weights(str(weights_path))
```

### Cause 4: Encoding Problem

**Symptom**: Peptides not encoded correctly
**Check**: Look at DEBUG output - first prediction should show all 4 class probabilities

### Cause 5: Wrong Filter Selected

**Symptom**: UI filter set to "Non-Flyers Only"
**Check**: In the "Peptide Table" tab, make sure filter is set to "All"

## Detailed Debugging

### Step 1: Check Model Loading

Add to `utils/prediction.py` after `load_model()`:
```python
# Test the model immediately
import numpy as np
test_input = np.array([[1, 8, 10, 17, 6, 1, 4, 16, 9] + [0] * 31], dtype=np.int32)
test_output = model.predict(test_input, verbose=0)[0]
print(f"DEBUG Model Test: {test_output}")
# Should NOT be [1, 0, 0, 0] or all zeros
```

### Step 2: Check Batch Prediction

In `streamlit_app.py`, after `predict_batch`:
```python
st.write("DEBUG: Sample predictions")
for p in predictions[:3]:
    st.write(f"  {p['sequence']}: {p['predicted_class']} (flyer={p['is_flyer']})")
```

### Step 3: Check DataFrame

After `create_summary_table`:
```python
st.write("DEBUG: DataFrame sample")
st.write(results_df[['Peptide', 'Predicted Class', 'Is Flyer']].head())
```

## If Nothing Works

If all tests pass but the app still fails:

### Nuclear Option: Restart Everything

```bash
# Stop Streamlit
# Kill all Python processes
pkill -9 python

# Clear all caches
rm -rf ~/.streamlit/cache
rm -rf __pycache__
find . -name "*.pyc" -delete

# Restart
streamlit run streamlit_app.py
```

### Check Dependencies

```bash
pip list | grep -E "tensorflow|dlomix|streamlit"
```

Should show:
- `tensorflow==2.15.x`
- `dlomix>=0.0.1`
- `streamlit==1.28.0`

### Fresh Virtual Environment

```bash
cd streamlit_app
python -m venv venv_fresh
source venv_fresh/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Report Back

When you run the app with debug output, share:

1. **The DEBUG output** (from st.write statements)
2. **The test_full_workflow.py output**
3. **Your environment**:
   ```bash
   python --version
   pip list | grep tensorflow
   ls -lh ../notebooks/output/weights/new_base_model/
   ```

This will help identify the exact issue!

## Expected Behavior

For hemoglobin alpha (HBA_HUMAN):
- Total peptides: 8
- Flyers: 7 (Strong: 4, Intermediate: 2, Weak: 1)
- Non-Flyers: 1

If you see this in tests but not in the app, it's definitely a caching/runtime issue.
