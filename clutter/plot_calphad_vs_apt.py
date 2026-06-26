import numpy as np
import matplotlib.pyplot as plt
import os
from pycalphad import Database, equilibrium, variables as v
import warnings
warnings.filterwarnings('ignore')

# Ensure figures directory exists
os.makedirs('figures', exist_ok=True)

# 1. Run real CALPHAD simulation to get compositions
print("Simulating isothermal equilibrium at 480°C using Pycalphad...")
DB_PATH = '2databases/mc_fe_v2062_clean.tdb'
db = Database(DB_PATH)

COMPONENTS = ['FE', 'CR', 'CO', 'NI', 'TI', 'MO', 'SI', 'C', 'VA']
PHASES = ['LIQUID', 'BCC_A2', 'BCC_B2', 'FCC_A1', 'HCP_A3', 'ETA', 'LAVES_PHASE', 'SIGMA', 'NITI2', 'M23C6', 'CHI_A12', 'MU_PHASE']

comp = {'CR': 0.12017, 'CO': 0.03855, 'NI': 0.07742, 'TI': 0.00593, 'MO': 0.02960, 'SI': 0.00202, 'C': 0.00009}

iso_result = equilibrium(
    db, COMPONENTS, PHASES,
    {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
     v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'],
     v.X('C'): comp['C'],
     v.T: 480 + 273.15, v.P: 101325}
)

def get_stable_Y(phase_name):
    for v_idx in range(iso_result.sizes['vertex']):
        ph = str(iso_result.Phase.squeeze().isel(vertex=v_idx).values)
        if phase_name == ph:
            return iso_result.Y.squeeze().isel(vertex=v_idx).values
    return None

def compute_phase_composition(phase_name):
    Y_vals = get_stable_Y(phase_name)
    if Y_vals is None:
        return {el: 0.0 for el in COMPONENTS if el != 'VA'}
        
    phase_obj = db.phases[phase_name]
    y_idx = 0
    moles = {el: 0.0 for el in COMPONENTS if el != 'VA'}
    total_moles_atoms = 0.0
    
    for subl_idx, subl_elements in enumerate(phase_obj.constituents):
        active_elements = sorted(list(set(subl_elements).intersection(set(COMPONENTS))))
        stoich = phase_obj.sublattices[subl_idx]
        
        va_frac = 0.0
        if 'VA' in active_elements:
            va_idx = active_elements.index('VA')
            va_frac = Y_vals[y_idx + va_idx]
            
        total_moles_atoms += stoich * (1.0 - va_frac)
        
        for el in active_elements:
            if el != 'VA':
                moles[el] += stoich * Y_vals[y_idx]
            y_idx += 1
                
    at_frac = {el: (moles[el] / total_moles_atoms) * 100 for el in moles}
    return at_frac

calphad_bcc = compute_phase_composition('BCC_A2')
calphad_eta = compute_phase_composition('ETA')

# Experimental APT values from Li et al. 2024
apt_bcc = {'FE': 72.5, 'CR': 11.5, 'NI': 6.5, 'MO': 4.0, 'TI': 1.5, 'CO': 5.0, 'SI': 0.5, 'C': 0.0}
apt_eta = {'FE': 1.4, 'CR': 1.0, 'NI': 72.4, 'MO': 0.3, 'TI': 23.8, 'CO': 1.0, 'SI': 0.1, 'C': 0.0}

elements = ['FE', 'NI', 'TI', 'CR', 'MO', 'CO', 'SI']

# 2. Plotting Grouped Bar Chart
print("Generating scientifically accurate comparison plot...")
x = np.arange(len(elements))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot Matrix (BCC)
calc_bcc_vals = [calphad_bcc[el] for el in elements]
exp_bcc_vals = [apt_bcc[el] for el in elements]

ax1.bar(x - width/2, calc_bcc_vals, width, label='CALPHAD Simulated', color='#1f77b4', edgecolor='black')
ax1.bar(x + width/2, exp_bcc_vals, width, label='APT Experimental', color='#ff7f0e', edgecolor='black')

ax1.set_ylabel('Concentration (at. %)', fontsize=12)
ax1.set_title('Matrix ($\\alpha$-Fe) Composition', fontsize=14)
ax1.set_xticks(x)
ax1.set_xticklabels(elements, fontsize=11)
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3)

# Plot Precipitate (ETA)
calc_eta_vals = [calphad_eta[el] for el in elements]
exp_eta_vals = [apt_eta[el] for el in elements]

ax2.bar(x - width/2, calc_eta_vals, width, label='CALPHAD Simulated', color='#1f77b4', edgecolor='black')
ax2.bar(x + width/2, exp_eta_vals, width, label='APT Experimental', color='#ff7f0e', edgecolor='black')

ax2.set_title('Precipitate ($\\eta$-Ni$_3$Ti) Composition', fontsize=14)
ax2.set_xticks(x)
ax2.set_xticklabels(elements, fontsize=11)
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3)

plt.suptitle('Thermodynamic Equilibrium (CALPHAD) vs Experimental Observations (APT)', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()

output_path = 'figures/calphad_vs_apt_composition.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Plot saved successfully to {output_path}")
