import json

notebook_path = 'notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb'
with open(notebook_path, 'r') as f:
    nb = json.load(f)

new_cells = []

# Cell 1: Markdown header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 4. Phase Compositions at 480°C\n",
        "\n",
        "**Paper equivalent:** Li et al. 2024, Fig 7d1 (APT compositions)\n",
        "\n",
        "Here we extract the composition of the ETA (Ni₃Ti) phase and the BCC_A2 (matrix) phase from our isothermal equilibrium calculation at 480°C to compare with the APT measurements."
    ]
})

# Cell 2: Python Code
code_src = """# Extracting phase compositions from the existing iso_result
def get_stable_Y(phase_name):
    # Find the vertex where the phase is stable (NP > 0)
    for v_idx in range(iso_result.sizes['vertex']):
        ph = str(iso_result.Phase.squeeze().isel(vertex=v_idx).values)
        if phase_name == ph:
            y_vals = iso_result.Y.squeeze().isel(vertex=v_idx).values
            return y_vals
    return None

def compute_phase_composition(phase_name):
    Y_vals = get_stable_Y(phase_name)
    if Y_vals is None:
        print(f"{phase_name} phase is not stable at 480°C.")
        return None
        
    # Get sublattices and stoichiometries from the database
    phase_obj = db.phases[phase_name]
    stoichiometries = phase_obj.sublattices
    
    print(f"--- {phase_name} Phase Raw Site Fractions ---")
    
    # Active elements in each sublattice (sorted alphabetically per pycalphad convention)
    y_idx = 0
    moles = {el: 0.0 for el in COMPONENTS if el != 'VA'}
    total_moles_atoms = 0.0
    
    for subl_idx, subl_elements in enumerate(phase_obj.constituents):
        active_elements = sorted(list(set(subl_elements).intersection(set(COMPONENTS))))
        stoich = stoichiometries[subl_idx]
        
        # Calculate how many moles of vacancies are in this sublattice
        va_frac = 0.0
        if 'VA' in active_elements:
            va_idx = active_elements.index('VA')
            va_frac = Y_vals[y_idx + va_idx]
            
        total_moles_atoms += stoich * (1.0 - va_frac)
        
        for el in active_elements:
            y = Y_vals[y_idx]
            y_idx += 1
            if y > 1e-10:
                print(f"  Sublattice {subl_idx} ({el}): {y:.6f}")
            if el != 'VA':
                moles[el] += stoich * y
                
    print(f"\\n--- {phase_name} Phase Overall Composition ---")
    at_frac = {}
    wt_frac = {}
    total_wt = 0.0
    
    for el in moles:
        at_frac[el] = moles[el] / total_moles_atoms
        if at_frac[el] > 1e-6:
            total_wt += at_frac[el] * AW[el]
            
    for el in moles:
        if at_frac[el] > 1e-6:
            wt_frac[el] = (at_frac[el] * AW[el]) / total_wt
            print(f"  {el:<2}: {at_frac[el]*100:>6.2f} at.%  |  {wt_frac[el]*100:>6.2f} wt.%")
            
    return at_frac

print("Using atomic weights:", AW, "\\n")
eta_comp = compute_phase_composition('ETA')
print("\\n" + "="*50 + "\\n")
bcc_comp = compute_phase_composition('BCC_A2')
"""
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" if i < len(code_src.split("\n"))-1 else line for i, line in enumerate(code_src.split("\n"))]
})

# Cell 3: Markdown table
markdown_table = """### CALPHAD vs. APT Composition Comparison

The following table compares the phase compositions predicted by CALPHAD at 480°C with the APT-measured core and matrix compositions from Li et al. 2024 (SA30000 sample, Fig 7d1).

*Note: The APT matrix values are visually estimated from the concentration plateau far from the precipitate, as precise numbers were not tabulated in the original paper.*

| Element | CALPHAD ETA (at.%) | APT Ni3Ti core (at.%) | CALPHAD BCC (at.%) | APT matrix (at.%, approximate) |
|---------|--------------------|-----------------------|--------------------|--------------------------------|
| Fe      | 1.58               | 1.4                   | 72.34              | 70-75                          |
| Co      | 0.00               | 1.0                   | 1.35               | 4-6                            |
| Ni      | 73.43              | 72.4                  | 7.62               | 5-8                            |
| Ti      | 24.98              | 23.8                  | 2.04               | 1-2                            |
| Mo      | 0.00               | 0.3                   | 4.42               | 3-5                            |
| Cr      | 0.00               | 1.0                   | 12.02              | 3-5                            |
| Si      | 0.00               | 0.1                   | 0.20               | <1                             |
| C       | 0.00               | -                     | 0.00               | -                              |
"""
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + "\n" if i < len(markdown_table.split("\n"))-1 else line for i, line in enumerate(markdown_table.split("\n"))]
})

nb['cells'].extend(new_cells)

with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)
