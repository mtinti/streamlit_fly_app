"""
Test the exact workflow used in the Streamlit app.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Mock streamlit
class MockStreamlit:
    @staticmethod
    def cache_resource(func):
        return func

sys.modules['streamlit'] = MockStreamlit()

print("="*70)
print("TESTING FULL STREAMLIT WORKFLOW")
print("="*70)

# Import exactly as the Streamlit app does
from utils import (
    parse_fasta,
    trypsin_digest,
    load_model,
    predict_batch,
    create_summary_table,
)

# Use the same example from the app
test_fasta = """>sp|P69905|HBA_HUMAN Hemoglobin subunit alpha
MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGH
GKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEF
TPAVHASLDKFLASVSTVLTSKYR"""

print("\n1. Parse FASTA...")
protein_id, protein_sequence = parse_fasta(test_fasta)
print(f"   ✅ Protein ID: {protein_id[:50]}...")
print(f"   ✅ Sequence length: {len(protein_sequence)}")

print("\n2. Trypsin digestion...")
peptides = trypsin_digest(protein_sequence, min_length=6, max_length=40)
print(f"   ✅ Found {len(peptides)} peptides")
for i, p in enumerate(peptides[:3]):
    print(f"      {i+1}. {p['sequence']} ({p['start']}-{p['end']})")

print("\n3. Load model...")
model = load_model()
print(f"   ✅ Model loaded")

print("\n4. Batch prediction...")
predictions = predict_batch(peptides, model)
print(f"   ✅ Generated {len(predictions)} predictions")

print("\n5. Check predictions...")
print("\nDetailed results:")
for i, pred in enumerate(predictions):
    print(f"\n{i+1}. {pred['sequence']} ({pred['start']}-{pred['end']})")
    print(f"   Predicted class: {pred['predicted_class']}")
    print(f"   Is flyer: {pred['is_flyer']}")
    print(f"   Probabilities:")
    for class_name, prob in pred['probabilities'].items():
        print(f"      {class_name}: {prob:.4f}")

print("\n6. Create summary table...")
results_df = create_summary_table(predictions)
print(f"   ✅ DataFrame created with {len(results_df)} rows")

print("\n7. Summary:")
print(results_df[['Peptide', 'Predicted Class', 'Is Flyer']])

# Count classes
print("\n8. Class distribution:")
class_counts = results_df['Predicted Class'].value_counts()
for class_name, count in class_counts.items():
    print(f"   {class_name}: {count}")

flyer_count = results_df['Is Flyer'].sum()
non_flyer_count = len(results_df) - flyer_count
print(f"\n   Flyers: {flyer_count}")
print(f"   Non-Flyers: {non_flyer_count}")

if flyer_count == 0:
    print("\n" + "="*70)
    print("❌ PROBLEM: All peptides are Non-Flyers!")
    print("="*70)
    print("\nThis matches your issue. Let me check the predictions in detail...")

    print("\nRaw probability outputs:")
    for pred in predictions[:3]:
        print(f"\n{pred['sequence']}:")
        print(f"   probabilities dict: {pred['probabilities']}")
        print(f"   predicted_class: {pred['predicted_class']}")
        print(f"   predicted_class_index: {pred.get('predicted_class_index', 'MISSING')}")
        print(f"   is_flyer: {pred['is_flyer']}")
else:
    print("\n" + "="*70)
    print("✅ WORKFLOW WORKS CORRECTLY")
    print("="*70)
    print("\nThe workflow produces the expected mixed results.")
    print("If you're seeing all Non-Flyers in the actual app, the issue")
    print("might be with:")
    print("  1. Streamlit caching")
    print("  2. Model not reloading properly")
    print("  3. Different input being used")
