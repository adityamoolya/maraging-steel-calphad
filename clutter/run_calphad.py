import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pycalphad import Database, equilibrium, variables as v
import warnings

DB_PATH = '2databases/mc_fe_v2062_clean.tdb'
db = Database(DB_PATH)

# Atomic weights
AW = {'FE': 55.845, 'NI': 58.693, 'CO': 58.933, 'MO': 95.94, 'TI': 47.867, 'CR': 51.996, 'SI': 28.085, 'C': 12.011}

# Weight fractions (Li et al. 2024: Fe-11.0Cr-4.0Co-8.0Ni-0.5Ti-5.0Mo-0.1Si-0.002C)
wt_frac = {'NI': 0.080, 'CO': 0.040, 'MO': 0.050, 'TI': 0.005, 'CR': 0.110, 'SI': 0.001, 'C': 0.00002}
wt_frac['FE'] = 1.0 - sum(wt_frac.values())

# Convert to mole fractions
moles = {el: wt_frac[el] / AW[el] for el in AW}
total_moles = sum(moles.values())
comp = {el: moles[el] / total_moles for el in moles}

print('Composition (mole fractions):')
for el, xf in comp.items():
    print(f'  X({el}) = {xf:.5f}')

COMPONENTS = ['FE', 'NI', 'CO', 'MO', 'TI', 'CR', 'SI', 'C', 'VA']
PHASES = [p for p in ['LIQUID', 'BCC_A2', 'FCC_A1', 'HCP_A3', 'ETA',
          'LAVES_PHASE', 'BCC_B2', 'NITI2', 'SIGMA', 'M23C6']
          if p in db.phases]
print(f'Phases to compute: {PHASES}')

T_MIN, T_MAX, T_STEP = 573, 1373, 10
T_range = np.arange(T_MIN, T_MAX + T_STEP, T_STEP)

print('Running equilibrium sweep...')
result_sweep = equilibrium(
    db, COMPONENTS, PHASES,
    {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
     v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'], v.X('C'): comp['C'],
     v.T: T_range, v.P: 101325}
)

phase_fracs = {}
for ph in PHASES:
    mask = result_sweep.Phase == ph
    frac = result_sweep.NP.where(mask).sum(dim='vertex').squeeze().values
    phase_fracs[ph] = np.nan_to_num(frac, nan=0.0)

combined = {}
combined['BCC (martensite)'] = phase_fracs.get('BCC_A2', 0) + phase_fracs.get('BCC_B2', 0)
combined['FCC (austenite)'] = phase_fracs.get('FCC_A1', 0)
for ph in ['ETA', 'LAVES_PHASE', 'NITI2', 'LIQUID', 'HCP_A3', 'SIGMA', 'M23C6']:
    if ph in phase_fracs:
        combined[ph] = phase_fracs[ph]

T_C = T_range - 273.15

fig, ax = plt.subplots(figsize=(10, 6))

COLORS = {'BCC (martensite)': '#2166ac', 'FCC (austenite)': '#d73027',
          'ETA': '#1a9641', 'LAVES_PHASE': '#a65628', 'LIQUID': '#984ea3',
          'HCP_A3': '#ff7f00', 'NITI2': '#e7298a', 'SIGMA': '#66a61e', 'M23C6': '#000000'}
LABELS = {'BCC (martensite)': r'$\alpha$-Fe (BCC)', 'FCC (austenite)': r'$\gamma$-Fe (FCC)',
          'ETA': r'$\eta$-Ni$_3$Ti (target)', 'LAVES_PHASE': 'Laves',
          'LIQUID': 'Liquid', 'HCP_A3': 'HCP', 'NITI2': 'NiTi$_2$',
          'SIGMA': 'Sigma', 'M23C6': 'M23C6'}

for ph, frac in combined.items():
    if isinstance(frac, (int, float)):
        continue
    if frac.max() > 0.001:
        ax.plot(T_C, frac, color=COLORS.get(ph, 'grey'), label=LABELS.get(ph, ph), linewidth=2)

T_480 = 480
ax.axvline(T_480, color='black', linestyle='--', linewidth=1.0, alpha=0.7)
ax.text(T_480+5, 0.92, 'Aging (480°C)', fontsize=8, rotation=90, va='top', alpha=0.8)

ax.set_xlabel('Temperature (°C)', fontsize=13)
ax.set_ylabel('Phase Fraction (mole)', fontsize=13)
ax.set_title('Equilibrium Phase Fractions vs Temperature\nFe-11Cr-8Ni-5Mo-4Co-0.5Ti-0.1Si-0.002C wt% (mc_fe_v2062_clean)', fontsize=11)
ax.set_xlim(T_C[0], T_C[-1]); ax.set_ylim(-0.02, 1.05)
ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
ax.legend(loc='center right', fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig1_phase_fraction_vs_T.png', dpi=150, bbox_inches='tight')

# Isothermal 480C
T_K = 480 + 273.15
res = equilibrium(db, COMPONENTS, PHASES,
    {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
     v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'], v.X('C'): comp['C'],
     v.T: T_K, v.P: 101325})

iso_summary = {}
iso_summary['Li et al. (480°C)'] = {}
for ph in PHASES:
    mask = res.Phase == ph
    frac = res.NP.where(mask).sum(dim='vertex').squeeze().values
    iso_summary['Li et al. (480°C)'][ph] = np.nan_to_num(frac, nan=0.0)

labels = ['Li et al. (480°C)']
bcc_fracs = [iso_summary[l].get('BCC_A2', 0) * 100 for l in labels]
fcc_fracs = [iso_summary[l].get('FCC_A1', 0) * 100 for l in labels]
eta_fracs = [iso_summary[l].get('ETA', 0) * 100 for l in labels]
laves_fracs = [iso_summary[l].get('LAVES_PHASE', 0) * 100 for l in labels]

x = np.arange(len(labels))
width = 0.2
fig, ax = plt.subplots(figsize=(8, 6))

rects1 = ax.bar(x - 1.5*width, bcc_fracs, width, label='BCC_A2', color='grey')
rects2 = ax.bar(x - 0.5*width, fcc_fracs, width, label='FCC_A1', color='grey', alpha=0.7)
rects3 = ax.bar(x + 0.5*width, eta_fracs, width, label=r'$\eta$-Ni$_3$Ti (target)', color='#1a9641')
rects4 = ax.bar(x + 1.5*width, laves_fracs, width, label='Laves', color='#a65628')

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        if height > 0.1:
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
autolabel(rects4)

ax.set_ylabel('Phase Fraction (mole)', fontsize=13)
ax.set_title('Isothermal Equilibrium\nFe-11Cr-8Ni-5Mo-4Co-0.5Ti-0.1Si-0.002C wt%', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12)
ax.set_ylim(0, 105)
ax.yaxis.set_major_formatter(ticker.PercentFormatter())
ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig2_isothermal_comparison.png', dpi=150, bbox_inches='tight')

print('Plots generated.')
for ph, f in iso_summary['Li et al. (480°C)'].items():
    if f > 0.001:
        print(f'{ph}: {f*100:.2f}%')
