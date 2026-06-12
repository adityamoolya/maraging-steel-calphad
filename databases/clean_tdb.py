import re

input_path = 'databases/mc_fe_v2062.tdb'
output_path = 'databases/mc_fe_v2062_clean.tdb'

print("Cleaning TDB file...")
non_standard_keywords = ['REFERENCE_ELEMENT', 'ADD_COMPOSITION_SET', 'ATTACH_CONTRIBUTION', 'CREATE_NEW_PHASE']

with open(input_path, 'r', encoding='latin-1') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
    in_skip_block = False
    for line in f_in:
        cleaned_line = line.strip()
        
        # Stop writing when we reach the bibliography list of references
        if cleaned_line.startswith('$ E) List of references') or cleaned_line.startswith('A00201-0'):
            print("Reached bibliography section. Stopping output.")
            break
            
        # Check for non-standard keywords
        is_non_standard = False
        for kw in non_standard_keywords:
            if cleaned_line.startswith(kw):
                is_non_standard = True
                break
        
        # Check if we are starting a PARAMETER HMVA block
        if cleaned_line.startswith('PARAMETER HMVA'):
            in_skip_block = True
            
        if is_non_standard or in_skip_block:
            f_out.write(f"$ Cleaned by script: {line}")
            # If the current line ends with a '!', it terminates the block/parameter statement
            if cleaned_line.endswith('!'):
                in_skip_block = False
        else:
            # Fix the semicolon typo in G_PHASE parameter definition if present
            if 'PARAMETER G(G_PHASE;FE:CU:SI;0)' in line:
                line = line.replace('PARAMETER G(G_PHASE;FE:CU:SI;0)', 'PARAMETER G(G_PHASE,FE:CU:SI;0)')
            
            # Fix the missing exclamation mark typo in LAVES_PHASE parameter
            if 'PARAMETER L(LAVES_PHASE,MN,TI:NI;0) 273.00 +70000; 6000.00  N' in line and not line.endswith('!'):
                line = line.replace('PARAMETER L(LAVES_PHASE,MN,TI:NI;0) 273.00 +70000; 6000.00  N', 'PARAMETER L(LAVES_PHASE,MN,TI:NI;0) 273.00 +70000; 6000.00  N !')
            
            # Fix temperature limit typo (double decimal point)
            if '6000.00.00' in line:
                line = line.replace('6000.00.00', '6000.00')
                
            # Fix PDMN_B2 syntax typos
            if '273.00 273' in line:
                line = line.replace('273.00 273', '273.00')
            if '; 6000.00  N ; 6000.00  N' in line:
                line = line.replace('; 6000.00  N ; 6000.00  N', '; 6000.00  N')
                
            # Fix constituent definition relic typo in MNB4
            if 'CONSTITUENT MNB4' in line and '> >> 1 !' in line:
                line = line.replace('> >> 1 !', '!')
                
            # Fix reference space typo in test koze10
            if 'REF:test koze10' in line:
                line = line.replace('REF:test koze10', 'REF:test_koze10')
                
            f_out.write(line)

print("Done. Saved to databases/mc_fe_v2062_clean.tdb")
