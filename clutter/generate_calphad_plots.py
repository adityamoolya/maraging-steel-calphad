import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
from pycalphad import Database, equilibrium, variables as v
import warnings
warnings.filterwarnings('ignore')

# 1. Setup
DB_PATH = '2databases/mc_fe_v2062_clean.tdb'
db = Database(DB_PATH)

COMPONENTS = ['FE', 'CR', 'CO', 'NI', 'TI', 'MO', 'SI', 'C', 'VA']
PHASES = ['LIQUID', 'BCC_A2', 'BCC_B2', 'FCC_A1', 'HCP_A3', 'ETA', 'LAVES_PHASE', 'SIGMA', 'NITI2', 'M23C6', 'CHI_A12', 'MU_PHASE']

comp = {'CR': 0.12017, 'CO': 0.03855, 'NI': 0.07742, 'TI': 0.00593, 'MO': 0.02960, 'SI': 0.00202, 'C': 0.00009}
comp_dict = {
    v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
    v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'],
    v.X('C'): comp['C'], v.P: 101325
}

# Ensure figures directory exists
os.makedirs('figures', exist_ok=True)

# 2. Phase Fraction vs Temperature
print("Computing equilibrium sweep: 300°C to 1100°C, step=10 K...")
T_MIN, T_MAX, T_STEP = 573, 1373, 10
T_range = np.arange(T_MIN, T_MAX + T_STEP, T_STEP)

conds_sweep = comp_dict.copy()
conds_sweep[v.T] = T_range

result_sweep = equilibrium(db, COMPONENTS, PHASES, conds_sweep)

phase_fracs = {}
for ph in PHASES:
    mask = result_sweep.Phase == ph
    frac = result_sweep.NP.where(mask).sum(dim='vertex').squeeze().values
    phase_fracs[ph] = np.nan_to_num(frac, nan=0.0)

combined = {}
combined['BCC (martensite)'] = phase_fracs.get('BCC_A2', 0) + phase_fracs.get('BCC_B2', 0)
combined['FCC (austenite)'] = phase_fracs.get('FCC_A1', 0)
for ph in ['ETA', 'LAVES_PHASE', 'NITI2', 'LIQUID', 'HCP_A3', 'SIGMA', 'MU_PHASE', 'CHI_A12', 'M23C6']:
    if ph in phase_fracs:
        combined[ph] = phase_fracs[ph]

T_C = T_range - 273.15

COLORS = {
    'BCC (martensite)': '#2166ac', 'FCC (austenite)': '#d73027',
    'ETA': '#1a9641', 'LAVES_PHASE': '#a65628', 'LIQUID': '#984ea3',
    'HCP_A3': '#ff7f00', 'NITI2': '#e7298a', 'SIGMA': '#66a61e',
    'MU_PHASE': '#e6ab02', 'M23C6': '#333333', 'CHI_A12': '#17becf'
}
LABELS = {
    'BCC (martensite)': r'$\alpha$-Fe (BCC matrix)',
    'FCC (austenite)': r'$\gamma$-Fe (FCC / RA)',
    'ETA': r'$\eta$-Ni$_3$Ti',
    'LAVES_PHASE': 'Laves (Mo-rich)',
    'LIQUID': 'Liquid',
    'HCP_A3': 'HCP',
    'NITI2': r'NiTi$_2$',
    'SIGMA': r'$\sigma$ phase (Fe-Cr)',
    'MU_PHASE': r'$\mu$ phase (Fe$_7$Mo$_6$)',
    'M23C6': r'M$_{23}$C$_6$',
    'CHI_A12': r'$\chi$ phase'
}

fig1, ax1 = plt.subplots(figsize=(10, 6))
for ph, frac in combined.items():
    if isinstance(frac, (int, float)): continue
    if frac.max() > 0.001:
        ax1.plot(T_C, frac, color=COLORS.get(ph, 'grey'), label=LABELS.get(ph, ph), linewidth=2)

ax1.axvline(480, color='black', linestyle='--', linewidth=1.0, alpha=0.7)
ax1.text(485, 0.92, 'Aging T = 480°C\n(Li et al.)', fontsize=8, rotation=90, va='top', alpha=0.8)
ax1.set_xlabel('Temperature (°C)', fontsize=13)
ax1.set_ylabel('Equilibrium Phase Fraction (mole)', fontsize=13)
ax1.set_title('CALPHAD Equilibrium Phase Fractions\nFe-11Cr-8Ni-5Mo-4Co-0.5Ti-0.1Si-0.002C wt% $\cdot$ mc_fe_v2062', fontsize=11)
ax1.set_xlim(T_C[0], T_C[-1])
ax1.set_ylim(-0.02, 1.05)
ax1.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
ax1.legend(loc='center right', fontsize=9, framealpha=0.9)
ax1.grid(True, alpha=0.3)
plt.tight_layout()
fig1.savefig('figures/fig1_phase_fraction_vs_T.png', dpi=150, bbox_inches='tight')
print('Figure saved: figures/fig1_phase_fraction_vs_T.png')

# 3. Isothermal Phase Fractions at 480°C
print("Computing isothermal equilibrium at 480°C...")
T_ISO = 480 + 273.15
conds_iso = comp_dict.copy()
conds_iso[v.T] = T_ISO

iso_result = equilibrium(db, COMPONENTS, PHASES, conds_iso)

iso_phases = {}
for ph in PHASES:
    mask = iso_result.Phase == ph
    frac_vals = iso_result.NP.where(mask).sum(dim='vertex').squeeze().values
    f = float(np.nan_to_num(frac_vals, nan=0.0))
    if f > 1e-6:
        iso_phases[ph] = f

labels_bar = []
fracs_bar = []
colors_bar = []
for ph, f in sorted(iso_phases.items(), key=lambda x: -x[1]):
    labels_bar.append(LABELS.get(ph, ph))
    fracs_bar.append(f)
    if ph in ['BCC_A2', 'BCC_B2']:
        colors_bar.append(COLORS['BCC (martensite)'])
    elif ph in ['FCC_A1']:
        colors_bar.append(COLORS['FCC (austenite)'])
    else:
        colors_bar.append(COLORS.get(ph, 'grey'))

fig2, ax2 = plt.subplots(figsize=(8, 5))
bars = ax2.bar(labels_bar, fracs_bar, color=colors_bar, edgecolor='black', linewidth=1)
for bar, frac in zip(bars, fracs_bar):
    height = bar.get_height()
    if height > 0.05:
        ax2.text(bar.get_x() + bar.get_width()/2., height/2, f'{frac*100:.2f}%',
                 ha='center', va='center', color='white', fontweight='bold', fontsize=11)
    else:
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{frac*100:.2f}%',
                 ha='center', va='bottom', color='black', fontweight='bold', fontsize=10)

ax2.set_ylabel('Mole Fraction', fontsize=12)
ax2.set_title('CALPHAD Phase Fractions at 480°C (Aging Temperature)', fontsize=13)
ax2.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
ax2.set_ylim(0, max(fracs_bar) * 1.15)
ax2.grid(axis='y', alpha=0.3)
plt.xticks(rotation=15, ha='right', fontsize=11)
plt.tight_layout()
fig2.savefig('figures/fig2_isothermal_480C.png', dpi=150, bbox_inches='tight')
print('Figure saved: figures/fig2_isothermal_480C.png')

print("All plots generated and saved successfully!")
