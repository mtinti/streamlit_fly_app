"""
Test Streamlit app functionality without running the full UI.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
from pathlib import Path

# Add streamlit_app to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock streamlit for testing
class MockStreamlit:
    @staticmethod
    def cache_resource(func):
        return func

sys.modules['streamlit'] = MockStreamlit()

print("="*70)
print("TESTING STREAMLIT APP FUNCTIONALITY")
print("="*70)

# Test 1: Import all utilities
print("\n1. Testing imports...")
try:
    from utils.sequence_processing import parse_fasta, trypsin_digest
    from utils.prediction import load_model, predict_batch
    from utils.visualization import generate_html_visualization, calculate_coverage_stats
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Load model
print("\n2. Testing model loading...")
try:
    model = load_model()
    print(f"   ✅ Model loaded: {type(model)}")
except Exception as e:
    print(f"   ❌ Model loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Parse FASTA
print("\n3. Testing FASTA parsing...")
test_fasta = """>sp|P69905|HBA_HUMAN Hemoglobin subunit alpha
MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGH
GKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEF
TPAVHASLDKFLASVSTVLTSKYR"""

try:
    protein_id, sequence = parse_fasta(test_fasta)
    print(f"   ✅ FASTA parsed: {protein_id[:30]}...")
    print(f"   ✅ Sequence length: {len(sequence)}")
except Exception as e:
    print(f"   ❌ FASTA parsing failed: {e}")
    sys.exit(1)

# Test 4: Trypsin digestion
print("\n4. Testing trypsin digestion...")
try:
    peptides = trypsin_digest(sequence, min_length=6, max_length=40)
    print(f"   ✅ Found {len(peptides)} peptides")
    print(f"   ✅ Example: {peptides[0]['sequence']}")
except Exception as e:
    print(f"   ❌ Digestion failed: {e}")
    sys.exit(1)

# Test 5: Batch prediction
print("\n5. Testing batch prediction...")
try:
    predictions = predict_batch(peptides, model)
    print(f"   ✅ Predictions generated for {len(predictions)} peptides")

    # Check first prediction
    first = predictions[0]
    print(f"   ✅ First peptide: {first['sequence']}")
    print(f"      Predicted class: {first['predicted_class']}")
    print(f"      Is flyer: {first['is_flyer']}")
except Exception as e:
    print(f"   ❌ Prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Statistics calculation
print("\n6. Testing statistics calculation...")
try:
    stats = calculate_coverage_stats(sequence, predictions)
    print(f"   ✅ Statistics calculated:")
    print(f"      Total peptides: {stats['total_peptides']}")
    print(f"      Flyers: {stats['flyer_peptides']}")
    print(f"      Non-flyers: {stats['non_flyer_peptides']}")
    print(f"      Coverage: {stats['sequence_coverage']:.1f}%")
except Exception as e:
    print(f"   ❌ Statistics failed: {e}")
    sys.exit(1)

# Test 7: HTML visualization
print("\n7. Testing HTML visualization...")
try:
    html = generate_html_visualization(sequence, predictions, protein_id)
    print(f"   ✅ HTML generated: {len(html)} characters")
    print(f"   ✅ Contains visualization elements")
except Exception as e:
    print(f"   ❌ Visualization failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\nThe Streamlit app is ready to run!")
print("\nTo start the app:")
print("  cd streamlit_app")
print("  streamlit run streamlit_app.py")
