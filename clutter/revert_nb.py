import nbformat
import sys

def fix_notebook(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    for cell in nb.cells:
        if cell.cell_type == 'code':
            source = cell.source
            if 'PHASES = list(db.phases.keys())' in source:
                new_source = source.replace(
                    "PHASES = list(db.phases.keys())",
                    "PHASES = ['LIQUID', 'BCC_A2', 'FCC_A1', 'HCP_A3', 'ETA', 'LAVES_PHASE', 'BCC_B2', 'NITI2', 'SIGMA', 'MU_PHASE']"
                )
                new_source = new_source.replace(
                    "print(f'\\nPhases to compute: All {len(PHASES)} available phases')",
                    "print(f'\\nPhases to compute: {PHASES}')"
                )
                cell.source = new_source
                
            if "phases_to_extract = ['BCC_A2', 'BCC_B2', 'FCC_A1', 'ETA', 'LAVES_PHASE', 'NITI2', 'LIQUID', 'HCP_A3', 'SIGMA', 'MU_PHASE', 'GAMMA_PRIME', 'C15_LAVES']" in source:
                new_source = source.replace(
                    "phases_to_extract = ['BCC_A2', 'BCC_B2', 'FCC_A1', 'ETA', 'LAVES_PHASE', 'NITI2', 'LIQUID', 'HCP_A3', 'SIGMA', 'MU_PHASE', 'GAMMA_PRIME', 'C15_LAVES']\nfor ph in phases_to_extract:\n    if ph not in result_sweep.Phase.values.flatten(): continue",
                    "for ph in PHASES:"
                )
                new_source = new_source.replace(
                    "['ETA', 'LAVES_PHASE', 'NITI2', 'LIQUID', 'HCP_A3', 'SIGMA', 'MU_PHASE', 'GAMMA_PRIME', 'C15_LAVES']",
                    "['ETA', 'LAVES_PHASE', 'NITI2', 'LIQUID', 'HCP_A3', 'SIGMA', 'MU_PHASE']"
                )
                cell.source = new_source

            if "COLORS = {'BCC (martensite)': '#2166ac'" in source:
                new_source = source.replace(
                    "'MU_PHASE': '#e6ab02', 'GAMMA_PRIME': '#1b7837', 'C15_LAVES': '#b15928'}",
                    "'MU_PHASE': '#e6ab02'}"
                )
                new_source = new_source.replace(
                    "'MU_PHASE': 'Mu', 'GAMMA_PRIME': r'$\\gamma^\\prime$-Ni$_3$(Ti,Al)', 'C15_LAVES': 'C15 Laves'}",
                    "'MU_PHASE': 'Mu'}"
                )
                cell.source = new_source

            if "for ph in phases_to_extract:" in source and "val = 0.0" in source:
                new_source = source.replace(
                    "for ph in phases_to_extract:\n        if ph not in res.Phase.values.flatten(): val = 0.0\n        else:",
                    "for ph in PHASES:"
                )
                cell.source = new_source
                
            if "print('\\n=== Precipitate Summary ===')" in source:
                new_source = source.replace(
                    "print('\\n=== Precipitate Summary ===')",
                    "print('\\n=== ETA (Ni3Ti) Summary ===')"
                )
                new_source = new_source.replace(
                    "    gp_val = iso_summary[label].get('GAMMA_PRIME', 0.0)\n    mu_val = iso_summary[label].get('MU_PHASE', 0.0)\n    c15_val = iso_summary[label].get('C15_LAVES', 0.0)\n    print(f'  {label}: ETA = {eta_val*100:.2f} mol%, GAMMA_PRIME = {gp_val*100:.2f} mol%, MU = {mu_val*100:.2f} mol%, C15 = {c15_val*100:.2f} mol%')",
                    "    print(f'  {label}: ETA = {eta_val:.4f} ({eta_val*100:.2f} mol%)')"
                )
                cell.source = new_source

            if "phases_to_plot = [ph for ph in phases_to_extract if any(" in source:
                new_source = source.replace(
                    "phases_to_plot = [ph for ph in phases_to_extract if any(",
                    "phases_to_plot = [ph for ph in PHASES if any("
                )
                cell.source = new_source

            if "Vm = {'BCC_A2': 7.09," in source:
                new_source = source.replace(
                    "'MU_PHASE': 7.5, 'GAMMA_PRIME': 10.80, 'C15_LAVES': 11.0}",
                    "'MU_PHASE': 7.5}"
                )
                cell.source = new_source

    with open(file_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

fix_notebook('notebooks/2.equilibrium.ipynb')
