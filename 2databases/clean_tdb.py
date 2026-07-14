"""
clean_tdb.py — Sanitize MatCalc mc_fe TDB for PyCalphad compatibility
=====================================================================
Converts mc_fe_v2062.tdb (MatCalc format) → mc_fe_v2062_clean.tdb (standard TDB).

Changes made:
  1. Comments out MatCalc-specific keywords:
     - REFERENCE_ELEMENT, ADD_COMPOSITION_SET, ATTACH_CONTRIBUTION, CREATE_NEW_PHASE
  2. Comments out PARAMETER HMVA(...) blocks (vacancy formation enthalpy, MatCalc extension)
  3. Fixes known syntax bugs in the original database:
     - G_PHASE semicolon→comma in parameter name
     - Missing '!' terminator on LAVES_PHASE parameter
     - Double decimal '6000.00.00' in temperature limit
     - Duplicate temperature prefix in PDMN_B2
     - Duplicate termination suffix in PDMN_B2
     - Relic '> >> 1' in MNB4 constituent definition
     - Space in reference name 'test koze10'
  4. Converts encoding from latin-1 → UTF-8
  5. Stops at bibliography section (not needed by pycalphad)

NO thermodynamic parameters (G, L, TC, BMAGN values) are modified.

Usage:
    python clean_tdb.py
"""

import re

input_path = 'mc_fe_v2062.tdb'
output_path = 'mc_fe_v2062_clean.tdb'

print("Cleaning TDB file: {} → {}".format(input_path, output_path))

# MatCalc-specific keywords to comment out
non_standard_keywords = [
    'REFERENCE_ELEMENT',
    'ADD_COMPOSITION_SET',
    'ATTACH_CONTRIBUTION',
    'CREATE_NEW_PHASE',
]

with open(input_path, 'r', encoding='latin-1') as f_in, \
     open(output_path, 'w', encoding='utf-8') as f_out:

    in_skip_block = False

    for line in f_in:
        cleaned_line = line.strip()

        # Stop writing when we reach the bibliography/reference list
        if cleaned_line.startswith('$ E) List of references') or \
           cleaned_line.startswith('A00201-0'):
            print("  Reached bibliography section. Stopping output.")
            break

        # Check for non-standard MatCalc keywords
        is_non_standard = any(cleaned_line.startswith(kw) for kw in non_standard_keywords)

        # Check if we are starting a PARAMETER HMVA block
        if cleaned_line.startswith('PARAMETER HMVA'):
            in_skip_block = True

        if is_non_standard or in_skip_block:
            # Comment out the line, preserving content for reference
            f_out.write("$ Cleaned by script: {}".format(line))
            # If the current line ends with '!', it terminates the block
            if cleaned_line.endswith('!'):
                in_skip_block = False
        else:
            # ── Syntax bug fixes ──

            # Fix 1: Semicolon→comma in G_PHASE parameter name
            if 'PARAMETER G(G_PHASE;FE:CU:SI;0)' in line:
                line = line.replace(
                    'PARAMETER G(G_PHASE;FE:CU:SI;0)',
                    'PARAMETER G(G_PHASE,FE:CU:SI;0)')

            # Fix 2: Missing '!' terminator on LAVES_PHASE parameter
            if 'PARAMETER L(LAVES_PHASE,MN,TI:NI;0) 273.00 +70000; 6000.00  N' in line \
               and not line.strip().endswith('!'):
                line = line.replace(
                    'PARAMETER L(LAVES_PHASE,MN,TI:NI;0) 273.00 +70000; 6000.00  N',
                    'PARAMETER L(LAVES_PHASE,MN,TI:NI;0) 273.00 +70000; 6000.00  N !')

            # Fix 3: Double decimal point in temperature limit
            if '6000.00.00' in line:
                line = line.replace('6000.00.00', '6000.00')

            # Fix 4: Duplicate temperature prefix in PDMN_B2
            if '273.00 273' in line:
                line = line.replace('273.00 273', '273.00')

            # Fix 5: Duplicate termination in PDMN_B2
            if '; 6000.00  N ; 6000.00  N' in line:
                line = line.replace('; 6000.00  N ; 6000.00  N', '; 6000.00  N')

            # Fix 6: Relic syntax in MNB4 constituent definition
            if 'CONSTITUENT MNB4' in line and '> >> 1 !' in line:
                line = line.replace('> >> 1 !', '!')

            # Fix 7: Space in reference name
            if 'REF:test koze10' in line:
                line = line.replace('REF:test koze10', 'REF:test_koze10')

            f_out.write(line)

print("Done. Output saved to: {}".format(output_path))
