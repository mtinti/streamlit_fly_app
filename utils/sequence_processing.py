"""Sequence processing utilities for protein analysis."""

import re


def parse_fasta(fasta_string):
    """
    Parse a FASTA format string and extract protein ID and sequence.

    Parameters
    ----------
    fasta_string : str
        Protein sequence in FASTA format

    Returns
    -------
    tuple
        (protein_id, sequence)

    Examples
    --------
    >>> fasta = ">sp|P12345|PROT_HUMAN Example protein\\nMVLSPADK"
    >>> protein_id, seq = parse_fasta(fasta)
    >>> print(protein_id)
    sp|P12345|PROT_HUMAN Example protein
    """
    lines = fasta_string.strip().split('\n')

    # Extract protein ID from header line
    if lines[0].startswith('>'):
        protein_id = lines[0][1:].strip()
        sequence = ''.join(lines[1:]).replace(' ', '').replace('\n', '').upper()
    else:
        protein_id = "Unknown"
        sequence = ''.join(lines).replace(' ', '').replace('\n', '').upper()

    return protein_id, sequence


def validate_sequence(sequence):
    """
    Validate that a sequence contains only valid amino acid characters.

    Parameters
    ----------
    sequence : str
        Protein sequence to validate

    Returns
    -------
    tuple
        (is_valid: bool, error_message: str or None)

    Examples
    --------
    >>> validate_sequence("MVLSPADK")
    (True, None)
    >>> validate_sequence("MVLSP4DK")
    (False, "Invalid characters found: 4")
    """
    valid_amino_acids = set('ACDEFGHIKLMNPQRSTVWY')
    sequence_set = set(sequence.upper())

    invalid_chars = sequence_set - valid_amino_acids

    if invalid_chars:
        return False, f"Invalid characters found: {', '.join(sorted(invalid_chars))}"

    if len(sequence) == 0:
        return False, "Sequence is empty"

    return True, None


def trypsin_digest(protein_sequence, min_length=6, max_length=40):
    """
    Perform in silico trypsin digestion of a protein sequence.

    Trypsin cleaves after K or R, except when followed by P.

    Parameters
    ----------
    protein_sequence : str
        Protein sequence to digest
    min_length : int
        Minimum peptide length to keep (default: 6)
    max_length : int
        Maximum peptide length to keep (default: 40, model limit)

    Returns
    -------
    list of dict
        List of peptides with their positions:
        [{"sequence": str, "start": int, "end": int, "length": int}, ...]

    Examples
    --------
    >>> peptides = trypsin_digest("MVLSPADKTNVKAAWGK", min_length=6)
    >>> peptides[0]['sequence']
    'MVLSPADK'
    """
    # Trypsin cleaves after K or R, but not before P
    # Use regex to find cleavage sites
    cleavage_pattern = r'(?<=[KR])(?!P)'

    # Find all cleavage positions
    cleavage_positions = [0]  # Start of protein
    for match in re.finditer(cleavage_pattern, protein_sequence):
        cleavage_positions.append(match.start())
    cleavage_positions.append(len(protein_sequence))  # End of protein

    # Extract peptides between cleavage sites
    peptides = []
    for i in range(len(cleavage_positions) - 1):
        start = cleavage_positions[i]
        end = cleavage_positions[i + 1]
        peptide_seq = protein_sequence[start:end]

        # Filter by length
        if min_length <= len(peptide_seq) <= max_length:
            peptides.append({
                "sequence": peptide_seq,
                "start": start,
                "end": end,
                "length": len(peptide_seq)
            })

    return peptides


def parse_multi_fasta(fasta_string):
    """
    Parse a multi-FASTA format string containing multiple protein sequences.

    Parameters
    ----------
    fasta_string : str
        Multi-FASTA format string

    Returns
    -------
    list of tuple
        List of (protein_id, sequence) tuples

    Examples
    --------
    >>> fasta = ">Protein1\\nMVLSPADK\\n>Protein2\\nACDEFGH"
    >>> proteins = parse_multi_fasta(fasta)
    >>> len(proteins)
    2
    """
    proteins = []
    current_id = None
    current_seq = []

    for line in fasta_string.strip().split('\n'):
        line = line.strip()
        if line.startswith('>'):
            # Save previous protein if exists
            if current_id is not None:
                proteins.append((current_id, ''.join(current_seq).upper()))
            # Start new protein
            current_id = line[1:]
            current_seq = []
        else:
            # Accumulate sequence
            current_seq.append(line.replace(' ', ''))

    # Save last protein
    if current_id is not None:
        proteins.append((current_id, ''.join(current_seq).upper()))

    return proteins
