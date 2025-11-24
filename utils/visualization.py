"""Visualization utilities for protein detectability results."""

import html

import pandas as pd


def generate_html_visualization(protein_sequence, peptides_with_predictions, protein_id="Unknown Protein"):
    """
    Generate an HTML visualization of protein sequence with color-coded tryptic peptides.

    Parameters
    ----------
    protein_sequence : str
        Full protein sequence
    peptides_with_predictions : list of dict
        List of peptides with predictions including 'sequence', 'start', 'end', 'is_flyer'
    protein_id : str
        Protein identifier for the title

    Returns
    -------
    str
        HTML string for display
    """
    # Define colors
    flyer_color = '#90EE90'      # Light green
    non_flyer_color = '#DDA0DD'  # Light purple
    no_coverage_color = '#E8E8E8'  # Light gray

    # Create a color map for each amino acid position
    seq_len = len(protein_sequence)
    colors = [no_coverage_color] * seq_len
    peptide_info = [''] * seq_len  # Store peptide info for tooltips

    # Color each amino acid based on its peptide's detectability
    for peptide in peptides_with_predictions:
        color = flyer_color if peptide['is_flyer'] else non_flyer_color
        tooltip = (
            f"Peptide: {peptide['sequence']}\\n"
            f"Class: {peptide['predicted_class']}\\n"
            f"Position: {peptide['start'] + 1}-{peptide['end']}"
        )
        for pos in range(peptide['start'], peptide['end']):
            colors[pos] = color
            peptide_info[pos] = tooltip

    # Generate HTML
    html_viz = f"""
    <div style="font-family: Arial, sans-serif; max-width: 1200px; margin: 20px auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <style>
        /* Explicit tooltip styling so hover info always renders inside the embedded iframe */
        .peptide-aa {{
            position: relative;
        }}
        .peptide-aa::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 110%;
            left: 50%;
            transform: translateX(-50%) translateY(6px);
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            padding: 6px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-family: 'Courier New', monospace;
            line-height: 1.3;
            white-space: pre-line;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
            opacity: 0;
            pointer-events: none;
            transition: opacity 120ms ease, transform 120ms ease;
            min-width: 170px;
            max-width: 240px;
            z-index: 10;
        }}
        .peptide-aa::before {{
            content: '';
            position: absolute;
            bottom: 102%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 6px;
            border-style: solid;
            border-color: rgba(0, 0, 0, 0.85) transparent transparent transparent;
            opacity: 0;
            transition: opacity 120ms ease;
            z-index: 9;
        }}
        .peptide-aa:hover::after,
        .peptide-aa:hover::before {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}
        </style>
        <h2 style="color: #333; text-align: center; margin-bottom: 20px;">
            Tryptic Peptide Detectability Map: {protein_id}
        </h2>

        <div style="margin-bottom: 20px; padding: 15px; background-color: white; border-radius: 5px;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 30px; height: 20px; background-color: {flyer_color}; border: 1px solid #ccc; border-radius: 3px;"></div>
                    <span style="font-size: 14px;">Flyer Peptides</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 30px; height: 20px; background-color: {non_flyer_color}; border: 1px solid #ccc; border-radius: 3px;"></div>
                    <span style="font-size: 14px;">Non-Flyer Peptides</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 30px; height: 20px; background-color: {no_coverage_color}; border: 1px solid #ccc; border-radius: 3px;"></div>
                    <span style="font-size: 14px;">Not Covered</span>
                </div>
            </div>
        </div>

        <div style="background-color: white; padding: 20px; border-radius: 5px; overflow-x: auto;">
    """

    # Display parameters
    chars_per_line = 60

    # Calculate number of lines
    num_lines = (seq_len + chars_per_line - 1) // chars_per_line

    # Generate each line
    for line_idx in range(num_lines):
        start_idx = line_idx * chars_per_line
        end_idx = min(start_idx + chars_per_line, seq_len)

        # Line container with fixed height
        html_viz += f"""
        <div style="display: flex; align-items: center; margin-bottom: 8px; min-height: 30px;">
            <div style="display: flex; gap: 0;">
        """

        # Add each amino acid
        for i in range(start_idx, end_idx):
            aa = protein_sequence[i]
            bg_color = colors[i]
            tooltip = peptide_info[i]
            # Escape tooltip to avoid breaking HTML attributes; preserve newlines for display
            safe_tooltip = html.escape(tooltip)

            # Create the amino acid span with tooltip
            html_viz += f"""
                <span class="peptide-aa" data-tooltip="{safe_tooltip}" style="
                    display: inline-block;
                    width: 16px;
                    height: 24px;
                    line-height: 24px;
                    text-align: center;
                    background-color: {bg_color};
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: bold;
                    color: #000;
                    border-right: 1px solid #fff;
                    cursor: pointer;
                ">{aa}</span>
            """

        # Add padding spaces to maintain consistent line length (60 chars)
        remaining = chars_per_line - (end_idx - start_idx)
        for _ in range(remaining):
            html_viz += f"""
                <span style="
                    display: inline-block;
                    width: 16px;
                    height: 24px;
                "></span>
            """

        # Close sequence div and add position range on the right
        html_viz += f"""
            </div>
            <div style="padding-left: 15px; font-family: 'Courier New', monospace; font-size: 12px; color: #666; white-space: nowrap;">
                {start_idx + 1}-{end_idx}
            </div>
        </div>
        """

    # Close main container
    html_viz += """
        </div>

        <div style="margin-top: 20px; padding: 15px; background-color: white; border-radius: 5px; font-size: 13px; color: #666;">
            <strong>Info:</strong> Hover over any colored amino acid to see its peptide, class, and position.
            Each line shows exactly 60 amino acids with consistent height and left alignment.
        </div>
    </div>
    """

    return html_viz


def create_summary_table(peptides_with_predictions):
    """
    Create a pandas DataFrame with peptide prediction results.

    Parameters
    ----------
    peptides_with_predictions : list of dict
        List of peptides with prediction results

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Peptide, Position, Length, Predicted Class,
        Non-Flyer, Weak Flyer, Intermediate Flyer, Strong Flyer
    """
    if not peptides_with_predictions:
        return pd.DataFrame()

    results_list = []
    for p in peptides_with_predictions:
        results_list.append({
            'Peptide': p['sequence'],
            'Position': f"{p['start']}-{p['end']}",
            'Length': p['length'],
            'Predicted Class': p['predicted_class'],
            'Non-Flyer': f"{p['probabilities']['Non-Flyer']:.3f}",
            'Weak Flyer': f"{p['probabilities']['Weak Flyer']:.3f}",
            'Intermediate Flyer': f"{p['probabilities']['Intermediate Flyer']:.3f}",
            'Strong Flyer': f"{p['probabilities']['Strong Flyer']:.3f}",
            'Is Flyer': p['is_flyer']
        })

    return pd.DataFrame(results_list)


def calculate_coverage_stats(protein_sequence, peptides_with_predictions):
    """
    Calculate coverage statistics for the protein.

    Parameters
    ----------
    protein_sequence : str
        Full protein sequence
    peptides_with_predictions : list of dict
        List of peptides with predictions

    Returns
    -------
    dict
        Dictionary with coverage statistics
    """
    # Calculate coverage
    covered_positions = set()
    for peptide in peptides_with_predictions:
        for pos in range(peptide['start'], peptide['end']):
            covered_positions.add(pos)

    coverage_percent = (len(covered_positions) / len(protein_sequence)) * 100

    # Count by class
    flyer_count = sum(1 for p in peptides_with_predictions if p['is_flyer'])
    non_flyer_count = len(peptides_with_predictions) - flyer_count

    # Calculate coverage by detectability
    flyer_positions = set()
    non_flyer_positions = set()

    for peptide in peptides_with_predictions:
        for pos in range(peptide['start'], peptide['end']):
            if peptide['is_flyer']:
                flyer_positions.add(pos)
            else:
                non_flyer_positions.add(pos)

    flyer_coverage = (len(flyer_positions) / len(protein_sequence)) * 100
    non_flyer_coverage = (len(non_flyer_positions) / len(protein_sequence)) * 100

    return {
        'total_peptides': len(peptides_with_predictions),
        'flyer_peptides': flyer_count,
        'non_flyer_peptides': non_flyer_count,
        'flyer_percentage': (flyer_count / len(peptides_with_predictions) * 100) if peptides_with_predictions else 0,
        'sequence_coverage': coverage_percent,
        'flyer_coverage': flyer_coverage,
        'non_flyer_coverage': non_flyer_coverage,
        'protein_length': len(protein_sequence)
    }
