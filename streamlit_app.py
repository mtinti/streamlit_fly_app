"""
Peptide Detectability Predictor
================================

A web application for predicting peptide detectability in mass spectrometry experiments.

Author: DLOmix Team
"""

# Suppress TensorFlow warnings (must be before importing tensorflow/dlomix)
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TF logging

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from utils import (
    parse_fasta,
    trypsin_digest,
    validate_sequence,
    load_model,
    predict_batch,
    generate_html_visualization,
    create_summary_table,
    calculate_coverage_stats
)


# Page configuration
st.set_page_config(
    page_title="Peptide Detectability Predictor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""

    # Header
    st.markdown('<h1 class="main-header">🧬 Peptide Detectability Predictor</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; font-size: 1.1rem; color: #666;">
    Predict which peptides from your protein will be detected by mass spectrometry
    </p>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This tool predicts peptide detectability using a deep learning model trained on proteomics data.

        **How it works:**
        1. Input your protein sequence (FASTA format)
        2. The tool performs in silico trypsin digestion
        3. Each peptide is classified as:
           - **Non-Flyer**: Low detection probability
           - **Weak Flyer**: Moderate detection
           - **Intermediate Flyer**: Good detection
           - **Strong Flyer**: High detection probability
        """)

        st.header("⚙️ Parameters")
        min_length = st.slider(
            "Min peptide length",
            min_value=4,
            max_value=20,
            value=6,
            help="Minimum peptide length to include after digestion"
        )

        max_length = st.slider(
            "Max peptide length",
            min_value=20,
            max_value=50,
            value=40,
            help="Maximum peptide length (model limit is 40)"
        )

        st.header("📊 Model Info")
        st.markdown("""
        - **Architecture**: BiGRU with Attention
        - **Training Data**: ProteomeTools + MAssIVE
        - **Framework**: TensorFlow 2.15
        - **Version**: 1.0
        """)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📝 Input Protein Sequence")

        # Example sequences
        examples = {
            "Human Hemoglobin Alpha": """>sp|P69905|HBA_HUMAN Hemoglobin subunit alpha OS=Homo sapiens
MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGH
GKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEF
TPAVHASLDKFLASVSTVLTSKYR""",
            "Human Insulin": """>sp|P01308|INS_HUMAN Insulin OS=Homo sapiens
MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAED
LQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN""",
            "Custom": ""
        }

        selected_example = st.selectbox(
            "Choose an example or enter custom sequence:",
            options=list(examples.keys())
        )

        if selected_example == "Custom":
            default_text = ">CustomProtein\nMVLSPADKTNVKAAWGK"
        else:
            default_text = examples[selected_example]

        fasta_input = st.text_area(
            "FASTA Sequence",
            value=default_text,
            height=200,
            help="Enter protein sequence in FASTA format (starting with >)"
        )

    with col2:
        st.header("🎯 Quick Stats")
        stats_placeholder = st.empty()

    # Predict button
    if st.button("🚀 Predict Detectability", type="primary", use_container_width=True):

        if not fasta_input.strip():
            st.error("⚠️ Please enter a protein sequence!")
            return

        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Step 1: Parse FASTA
            status_text.text("📖 Parsing FASTA sequence...")
            progress_bar.progress(10)

            protein_id, protein_sequence = parse_fasta(fasta_input)

            # Step 2: Validate sequence
            status_text.text("✅ Validating sequence...")
            progress_bar.progress(20)

            is_valid, error_msg = validate_sequence(protein_sequence)
            if not is_valid:
                st.error(f"❌ Invalid sequence: {error_msg}")
                progress_bar.empty()
                status_text.empty()
                return

            # Step 3: Trypsin digestion
            status_text.text("✂️ Performing trypsin digestion...")
            progress_bar.progress(30)

            peptides = trypsin_digest(protein_sequence, min_length, max_length)

            if not peptides:
                st.warning(f"⚠️ No peptides found between {min_length}-{max_length} amino acids!")
                progress_bar.empty()
                status_text.empty()
                return

            # Step 4: Load model
            status_text.text("🤖 Loading model...")
            progress_bar.progress(40)

            model = load_model()

            # Step 5: Predict
            status_text.text(f"🔮 Predicting detectability for {len(peptides)} peptides...")
            progress_bar.progress(50)

            predictions = predict_batch(peptides, model)

            # Step 6: Calculate statistics
            status_text.text("📊 Calculating statistics...")
            progress_bar.progress(80)

            stats = calculate_coverage_stats(protein_sequence, predictions)

            # Step 7: Generate visualizations
            status_text.text("🎨 Generating visualizations...")
            progress_bar.progress(90)

            html_viz = generate_html_visualization(protein_sequence, predictions, protein_id)
            results_df = create_summary_table(predictions)

            progress_bar.progress(100)
            status_text.text("✅ Complete!")

            # Display results
            st.success(f"✅ Successfully analyzed {stats['total_peptides']} tryptic peptides!")

            # Statistics cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Peptides",
                    stats['total_peptides'],
                    help="Number of tryptic peptides found"
                )

            with col2:
                st.metric(
                    "Flyer Peptides",
                    stats['flyer_peptides'],
                    f"{stats['flyer_percentage']:.1f}%",
                    help="Peptides with good detection probability"
                )

            with col3:
                st.metric(
                    "Non-Flyer Peptides",
                    stats['non_flyer_peptides'],
                    help="Peptides with low detection probability"
                )

            with col4:
                st.metric(
                    "Sequence Coverage",
                    f"{stats['sequence_coverage']:.1f}%",
                    help="Percentage of protein covered by peptides"
                )

            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["🗺️ Protein Map", "📊 Peptide Table", "💾 Download"])

            with tab1:
                st.subheader("Interactive Protein Detectability Map")
                # Use components.html to render the raw HTML rather than showing it as escaped markdown
                components.html(html_viz, height=650, scrolling=True)

                st.info("""
                **Legend:**
                - 🟢 **Light Green**: Flyer peptides (detectable)
                - 🟣 **Light Purple**: Non-Flyer peptides (low detection)
                - ⚪ **Light Gray**: Not covered (peptide too short/long)

                💡 **Tip**: Hover over amino acids to see peptide details!
                """)

            with tab2:
                st.subheader("Detailed Peptide Predictions")

                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    filter_class = st.multiselect(
                        "Filter by class:",
                        options=['Non-Flyer', 'Weak Flyer', 'Intermediate Flyer', 'Strong Flyer'],
                        default=['Non-Flyer', 'Weak Flyer', 'Intermediate Flyer', 'Strong Flyer']
                    )
                with col2:
                    filter_flyer = st.radio(
                        "Show:",
                        options=['All', 'Flyers Only', 'Non-Flyers Only'],
                        horizontal=True
                    )

                # Apply filters
                filtered_df = results_df.copy()
                if filter_class:
                    filtered_df = filtered_df[filtered_df['Predicted Class'].isin(filter_class)]

                if filter_flyer == 'Flyers Only':
                    filtered_df = filtered_df[filtered_df['Is Flyer'] == True]
                elif filter_flyer == 'Non-Flyers Only':
                    filtered_df = filtered_df[filtered_df['Is Flyer'] == False]

                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(f"Showing {len(filtered_df)} of {len(results_df)} peptides")

            with tab3:
                st.subheader("Download Results")

                col1, col2 = st.columns(2)

                with col1:
                    # Download CSV
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{protein_id.replace(' ', '_')}_detectability.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col2:
                    # Download HTML
                    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Protein Detectability Map - {protein_id}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    {html_viz}
</body>
</html>"""
                    st.download_button(
                        label="📥 Download HTML",
                        data=full_html,
                        file_name=f"{protein_id.replace(' ', '_')}_detectability.html",
                        mime="text/html",
                        use_container_width=True
                    )

                st.markdown("---")
                st.markdown("""
                **File Descriptions:**
                - **CSV**: Spreadsheet with all peptide predictions and probabilities
                - **HTML**: Interactive visualization you can open in any web browser
                """)

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            import traceback
            with st.expander("Show detailed error"):
                st.code(traceback.format_exc())

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Powered by <strong>DLOmix</strong> |
        <a href="https://github.com/wilhelm-lab/dlomix" target="_blank">GitHub</a> |
        <a href="https://dlomix.readthedocs.io" target="_blank">Documentation</a></p>
        <p>Model trained on ProteomeTools and MAssIVE datasets</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
