import json

with open("notebooks/2.equilibrium.ipynb", "r") as f:
    nb = json.load(f)

# Find the cell with the composition
for cell in nb["cells"]:
    if cell["cell_type"] == "markdown":
        source = "".join(cell["source"])
        if "Nominal alloy composition" in source:
            new_source = """# Notebook 2: Equilibrium Calculations

**Reference:** Li et al. 2024 — "Evolution and strengthening of nanoprecipitates in a high strength maraging stainless steel", Materials Science & Engineering A 915 (2024) 147198.

**Database:** `mc_fe_v2062_clean.tdb`  

## Objectives

This notebook performs equilibrium thermodynamic calculations for the maraging steel composition reported by Li et al. The objectives are:

1. Calculate phase fractions over a temperature range from **300°C to 1100°C**.
2. Perform isothermal equilibrium calculations at **480°C**.
3. Compare the predicted equilibrium phases with observations reported in the literature.

## Alloy Composition

Nominal alloy composition (wt.%):

| Element | Composition (wt.%) |
|----------|---------------------|
| Cr | 11.0 |
| Ni | 8.0 |
| Mo | 5.0 |
| Co | 4.0 |
| Ti | 0.5 |
| Si | 0.1 |
| C  | 0.002 |
| Fe | Balance |

The composition already sums correctly for the alloy system considered, so **no renormalization is required**.

## 0. Imports and Setup"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]
    elif cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "AW = {'FE': 55.845" in source:
            new_source = """
DB_PATH = '../2databases/mc_fe_v2062_clean.tdb'
from pycalphad import Database
db = Database(DB_PATH)

assert 'ETA' in db.phases, 'ETA (Ni3Ti) phase not found'
print('Database loaded successfully.')
print(f'Phases available: {sorted(db.phases.keys())}')

# Check for Cr, Si, C in elements
elements = list(db.elements)
print(f'Elements in DB: {elements}')
missing = [el for el in ['CR', 'SI', 'C'] if el not in elements]
if missing:
    print(f'WARNING: Elements missing from DB: {missing}')

# Atomic weights
AW = {'FE': 55.845, 'NI': 58.693, 'CO': 58.933, 'MO': 95.94, 'TI': 47.867, 'CR': 51.996, 'SI': 28.085, 'C': 12.011}

# Weight fractions (Li et al. 2024: Fe-11.0Cr-4.0Co-8.0Ni-0.5Ti-5.0Mo-0.1Si-0.002C)
wt_frac = {'NI': 0.080, 'CO': 0.040, 'MO': 0.050, 'TI': 0.005, 'CR': 0.110, 'SI': 0.001, 'C': 0.00002}
wt_frac['FE'] = 1.0 - sum(wt_frac.values())

# Convert to mole fractions
moles = {el: wt_frac[el] / AW[el] for el in AW}
total_moles = sum(moles.values())
comp = {el: moles[el] / total_moles for el in moles}

print(f'\\nComposition (mole fractions):')
for el, xf in comp.items():
    print(f'  X({el}) = {xf:.5f}')

# Components and phases
COMPONENTS = ['FE', 'NI', 'CO', 'MO', 'TI', 'CR', 'SI', 'C', 'VA']

# NOTE: Mu phase (Fe7Mo6) is suppressed as it tends to dominate over ETA in this DB
PHASES = [p for p in ['LIQUID', 'BCC_A2', 'FCC_A1', 'HCP_A3', 'ETA',
          'LAVES_PHASE', 'BCC_B2', 'NITI2', 'SIGMA', 'M23C6']
          if p in db.phases]
print(f'\\nPhases to compute: {PHASES}')

# ## Step 1 — Phase Fraction vs Temperature (300°C – 1100°C)
"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]
        elif "result_sweep = equilibrium" in source:
            new_source = """
T_MIN, T_MAX, T_STEP = 573, 1373, 10  # 300C to 1100C
T_range = np.arange(T_MIN, T_MAX + T_STEP, T_STEP)

print('Running equilibrium sweep... (this may take several minutes with 8 components)')

result_sweep = equilibrium(
    db, COMPONENTS, PHASES,
    {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
     v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'], v.X('C'): comp['C'],
     v.T: T_range, v.P: 101325}
)

print('Sweep complete.')
"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]
        elif "fig, ax = plt.subplots" in source and "COLORS =" in source:
            new_source = """
# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 6))

COLORS = {'BCC (martensite)': '#2166ac', 'FCC (austenite)': '#d73027',
          'ETA': '#1a9641', 'LAVES_PHASE': '#a65628', 'LIQUID': '#984ea3',
          'HCP_A3': '#ff7f00', 'NITI2': '#e7298a', 'SIGMA': '#66a61e', 'MU_PHASE': '#e6ab02', 'M23C6': '#000000'}
LABELS = {'BCC (martensite)': r'$\\alpha$-Fe (BCC)', 'FCC (austenite)': r'$\\gamma$-Fe (FCC)',
          'ETA': r'$\\eta$-Ni$_3$Ti (target)', 'LAVES_PHASE': 'Laves',
          'LIQUID': 'Liquid', 'HCP_A3': 'HCP', 'NITI2': 'NiTi$_2$',
          'SIGMA': 'Sigma', 'MU_PHASE': 'Mu', 'M23C6': 'M23C6'}

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
ax.set_title('Equilibrium Phase Fractions vs Temperature\\nFe-11Cr-8Ni-5Mo-4Co-0.5Ti-0.1Si-0.002C wt% (mc_fe_v2062_clean)', fontsize=11)
ax.set_xlim(T_C[0], T_C[-1]); ax.set_ylim(-0.02, 1.05)
ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
ax.legend(loc='center right', fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../figures/fig1_phase_fraction_vs_T.png', dpi=150, bbox_inches='tight')
plt.show()
print('Figure saved.')
"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]
        elif "get_phase_frac_at_T" in source:
            new_source = """
# --- Key values from sweep ---
def get_phase_frac_at_T(phase, T_celsius):
    idx = np.argmin(np.abs(T_C - T_celsius))
    return phase_fracs.get(phase, np.zeros_like(T_C))[idx]

print('=== Key Phase Fractions ===')
for T in [480, 840]:
    print(f'  At {T}°C : ETA(Ni3Ti) = {get_phase_frac_at_T("ETA", T):.4f}')

eta_frac = phase_fracs.get('ETA', np.zeros_like(T_C))
solvus = T_C[eta_frac > 0.001]
if len(solvus) > 0:
    print(f'  Ni3Ti solvus (approx): {solvus.max():.0f} °C')
    print(f'  Ni3Ti stable between:  {solvus.min():.0f} °C and {solvus.max():.0f} °C')
else:
    print('  WARNING: ETA phase never exceeds 0.001')

# ## Step 2 — Isothermal Calculations at 480°C
"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]
        elif "T_ISOTHERMAL =" in source:
            new_source = """
T_ISOTHERMAL = {'Li et al. (480°C)': 480+273.15}
iso_results = {}

for label, T_K in T_ISOTHERMAL.items():
    print(f'Computing {label}...')
    res = equilibrium(db, COMPONENTS, PHASES,
        {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
         v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'], v.X('C'): comp['C'],
         v.T: T_K, v.P: 101325})
    iso_results[label] = res
    print('  Done.')

print('\\nIsothermal calculations complete.')
"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]
        elif "fig, ax = plt.subplots" in source and "Isothermal Equilibrium" in source:
            new_source = """
# --- Isothermal Bar Chart ---
# We will just plot for 480C
labels = ['Li et al. (480°C)']

bcc_fracs = [iso_summary[l].get('BCC_A2', 0) * 100 for l in labels]
fcc_fracs = [iso_summary[l].get('FCC_A1', 0) * 100 for l in labels]
eta_fracs = [iso_summary[l].get('ETA', 0) * 100 for l in labels]
mu_fracs = [iso_summary[l].get('MU_PHASE', 0) * 100 for l in labels]

x = np.arange(len(labels))
width = 0.2

fig, ax = plt.subplots(figsize=(8, 6))

rects1 = ax.bar(x - 1.5*width, bcc_fracs, width, label='BCC_A2', color='grey')
rects2 = ax.bar(x - 0.5*width, fcc_fracs, width, label='FCC_A1', color='grey', alpha=0.7)
rects3 = ax.bar(x + 0.5*width, eta_fracs, width, label='$\\eta$-Ni$_3$Ti (target)', color='#1a9641')
rects4 = ax.bar(x + 1.5*width, mu_fracs, width, label='Mu', color='#e6ab02')

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
ax.set_title('Isothermal Equilibrium\\nFe-11Cr-8Ni-5Mo-4Co-0.5Ti-0.1Si-0.002C wt%', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12)
ax.set_ylim(0, 105)
ax.yaxis.set_major_formatter(ticker.PercentFormatter())

ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../figures/fig2_isothermal_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
"""
            cell["source"] = [line + "\n" if not line.endswith("\n") else line for line in new_source.split("\n")]

with open("notebooks/2.equilibrium.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
