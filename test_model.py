"""Test script to verify model loading and predictions."""

import sys
import numpy as np
import tensorflow as tf
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.prediction import load_model, predict_peptide, AA_TO_INT, CLASSES_LABELS


def test_model_loading():
    """Test that model loads correctly."""
    print("="*60)
    print("Testing Model Loading")
    print("="*60)

    try:
        model = load_model()
        print("✅ Model loaded successfully!")
        print(f"Model type: {type(model)}")
        print(f"Model inputs: {model.inputs}")
        print(f"Model outputs: {model.outputs}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_predictions(model):
    """Test that predictions work correctly."""
    print("\n" + "="*60)
    print("Testing Predictions")
    print("="*60)

    # Test peptides with known characteristics
    test_peptides = [
        "LILTGAESK",      # Should be a flyer (good peptide)
        "PEPTIDESEQ",     # Should be non-flyer (poor peptide)
        "MVLSPADK",       # Short peptide
        "ACDEFGHIKLMNPQRSTVWY",  # Contains all amino acids
    ]

    for peptide in test_peptides:
        print(f"\nTesting: {peptide}")
        try:
            result = predict_peptide(peptide, model)

            print(f"  Predicted Class: {result['predicted_class']}")
            print(f"  Is Flyer: {result['is_flyer']}")
            print(f"  Probabilities:")
            for class_name, prob in result['probabilities'].items():
                print(f"    {class_name}: {prob:.4f}")

            # Verify probabilities sum to 1
            prob_sum = sum(result['probabilities'].values())
            if abs(prob_sum - 1.0) < 0.01:
                print(f"  ✅ Probabilities sum correctly: {prob_sum:.4f}")
            else:
                print(f"  ⚠️  Probabilities don't sum to 1: {prob_sum:.4f}")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()


def test_model_architecture(model):
    """Test model architecture details."""
    print("\n" + "="*60)
    print("Model Architecture Details")
    print("="*60)

    print(f"\nNumber of layers: {len(model.layers)}")
    print("\nLayer details:")
    for i, layer in enumerate(model.layers):
        print(f"  {i}: {layer.name} ({layer.__class__.__name__})")
        if hasattr(layer, 'output_shape'):
            print(f"      Output shape: {layer.output_shape}")


def test_direct_inference(model):
    """Test direct model inference with dummy input."""
    print("\n" + "="*60)
    print("Testing Direct Inference")
    print("="*60)

    # Create dummy input (batch_size=1, seq_len=40)
    dummy_input = np.array([[1, 2, 3, 4, 5] + [0] * 35], dtype=np.int32)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Input dtype: {dummy_input.dtype}")

    try:
        # Suppress TensorFlow warnings temporarily
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            output = model.predict(dummy_input, verbose=0)

        print(f"Output shape: {output.shape}")
        print(f"Output dtype: {output.dtype}")
        print(f"Output range: [{output.min():.4f}, {output.max():.4f}]")
        print(f"Output sum (should be ~1 for softmax): {output.sum():.4f}")
        print("✅ Direct inference works!")

    except Exception as e:
        print(f"❌ Error during inference: {e}")
        import traceback
        traceback.print_exc()


def compare_with_notebook_model():
    """Compare with the model from the notebook."""
    print("\n" + "="*60)
    print("Comparing with Notebook Model")
    print("="*60)

    notebook_model_path = Path(__file__).parent.parent / "notebooks" / "output" / "saved_models" / "detectability_model"

    if notebook_model_path.exists():
        try:
            print(f"Loading notebook model from: {notebook_model_path}")
            notebook_model = tf.keras.models.load_model(str(notebook_model_path))

            # Test same input on both models
            test_input = np.array([[1, 8, 10, 17, 6, 1, 4, 16, 9] + [0] * 31], dtype=np.int32)

            app_model = load_model()

            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                notebook_output = notebook_model.predict(test_input, verbose=0)
                app_output = app_model.predict(test_input, verbose=0)

            print("\nNotebook model output:", notebook_output[0])
            print("App model output:     ", app_output[0])

            diff = np.abs(notebook_output - app_output).max()
            print(f"\nMax difference: {diff:.10f}")

            if diff < 1e-6:
                print("✅ Models produce identical outputs!")
            else:
                print("⚠️  Models produce different outputs!")

        except Exception as e:
            print(f"Could not compare: {e}")
    else:
        print("Notebook model not found - skipping comparison")


def main():
    """Run all tests."""
    print("\n" + "🧪 Model Verification Tests".center(60, "="))
    print()

    # Test 1: Load model
    model = test_model_loading()
    if model is None:
        print("\n❌ Model loading failed - cannot continue tests")
        return

    # Test 2: Architecture
    test_model_architecture(model)

    # Test 3: Direct inference
    test_direct_inference(model)

    # Test 4: Predictions
    test_predictions(model)

    # Test 5: Compare with notebook
    compare_with_notebook_model()

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

    print("\n📝 Summary:")
    print("The TensorFlow warnings you see are related to GRU control flow")
    print("and are generally harmless. They occur because:")
    print("  1. The model uses Bidirectional GRU layers")
    print("  2. GRU layers have return_sequences and return_state")
    print("  3. TensorFlow creates control flow graphs for these")
    print("\nAs long as predictions are working correctly (which they should be)")
    print("these warnings can be safely ignored.")


if __name__ == "__main__":
    main()
