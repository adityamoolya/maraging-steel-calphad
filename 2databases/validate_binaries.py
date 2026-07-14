"""
Multi-Binary Phase Diagram Validation Suite
============================================
Validates mc_fe_v2062_clean.tdb against well-known binary phase diagrams
relevant to maraging steels:
  1. Fe-Cr  (sigma, gamma loop, BCC miscibility gap)
  2. Fe-Ni  (FCC stabilisation, gamma loop closure, ordering)
  3. Fe-Ti  (Laves phase Fe2Ti, beta-Ti BCC loop)
  4. Fe-Mo  (sigma/mu/R-phase at intermediate T)
  5. Ni-Ti  (eta-Ni3Ti precipitate phase)

Requires: pycalphad, numpy, matplotlib (conda env: struct)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mc
from pycalphad import Database, equilibrium, variables as v
import warnings
warnings.filterwarnings('ignore')

DB_FILE = "mc_fe_v2062_clean.tdb"
db = Database(DB_FILE)
all_db_phases = list(db.phases.keys())
print("Database loaded: {} phases".format(len(all_db_phases)))

# ── Helper function ───────────────────────────────────────────────────────────
def compute_phase_map(db, components, phases, x_var, x_vals, t_vals):
    """Run equilibrium grid and extract phase map."""
    conds = {
        v.X(x_var): x_vals,
        v.T: t_vals,
        v.P: 101325,
        v.N: 1,
    }
    result = equilibrium(db, components, phases, conds, output="GM")

    np_vals = result.NP.values
    phase_vals = result.Phase.values
    t_celsius = t_vals - 273.15

    phase_map = np.full((len(t_vals), len(x_vals)), "", dtype=object)
    phase_names = set()

    for i in range(len(t_vals)):
        for j in range(len(x_vals)):
            try:
                nf = np_vals[0, 0, i, j, :]
                ph = phase_vals[0, 0, i, j, :]
                active = []
                for k in range(len(nf)):
                    pname = str(ph[k]).strip()
                    frac = float(nf[k]) if not np.isnan(nf[k]) else 0.0
                    if pname and pname != '' and frac > 0.01:
                        active.append(pname)
                label = "+".join(sorted(set(active))) if active else "UNKNOWN"
                phase_map[i, j] = label
                phase_names.update(active)
            except Exception:
                phase_map[i, j] = "UNKNOWN"

    return phase_map, phase_names, t_celsius


def plot_binary(ax, phase_map, phase_names, x_vals, t_celsius, x_label, title, 
                highlight_phases=None):
    """Plot a phase map on the given axes."""
    unique_labels = sorted(set(phase_map.flatten()))
    cmap = plt.cm.get_cmap("tab20", max(len(unique_labels), 2))
    label_to_idx = {lbl: i for i, lbl in enumerate(unique_labels)}

    img_data = np.zeros((len(t_celsius), len(x_vals), 3))
    for i in range(len(t_celsius)):
        for j in range(len(x_vals)):
            lbl = phase_map[i, j]
            col = cmap(label_to_idx.get(lbl, 0))
            img_data[i, j] = col[:3]

    ax.imshow(img_data, origin="lower", aspect="auto",
              extent=[x_vals[0], x_vals[-1], t_celsius[0], t_celsius[-1]])
    ax.set_xlabel(x_label, fontsize=10)
    ax.set_ylabel("Temperature (°C)", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")

    patches = []
    for lbl in sorted(unique_labels):
        if lbl == "UNKNOWN":
            continue
        col = cmap(label_to_idx[lbl])
        patches.append(mpatches.Patch(color=col, label=lbl))
    ax.legend(handles=patches, loc="upper left", fontsize=6, framealpha=0.85,
              ncol=1)

    return unique_labels


# ── Define binary systems ─────────────────────────────────────────────────────
systems = [
    {
        "name": "Fe-Cr",
        "components": ["FE", "CR", "VA"],
        "phases": ["BCC_A2", "FCC_A1", "SIGMA", "LIQUID"],
        "x_var": "CR",
        "x_label": "Mole Fraction Cr",
        "checks": [
            ("SIGMA phase present", lambda pm, tc, xv: 
                any("SIGMA" in pm[i,j] for i in range(len(tc)) for j in range(len(xv)))),
            ("FCC gamma loop (Fe-rich, >800°C)", lambda pm, tc, xv:
                any("FCC_A1" in pm[i,j] for i,t in enumerate(tc) if t>800 
                    for j,x in enumerate(xv) if x<0.15)),
            ("LIQUID at high T", lambda pm, tc, xv:
                any("LIQUID" in pm[i,j] for i,t in enumerate(tc) if t>1400 
                    for j in range(len(xv)))),
        ]
    },
    {
        "name": "Fe-Ni",
        "components": ["FE", "NI", "VA"],
        "phases": ["BCC_A2", "FCC_A1", "LIQUID"],
        "x_var": "NI",
        "x_label": "Mole Fraction Ni",
        "checks": [
            ("FCC dominant at high Ni", lambda pm, tc, xv:
                any("FCC_A1" in pm[i,j] for i,t in enumerate(tc) if 600<t<1000 
                    for j,x in enumerate(xv) if x>0.5)),
            ("BCC at low Ni, low T", lambda pm, tc, xv:
                any("BCC_A2" in pm[i,j] for i,t in enumerate(tc) if t<500 
                    for j,x in enumerate(xv) if x<0.1)),
            ("LIQUID at high T", lambda pm, tc, xv:
                any("LIQUID" in pm[i,j] for i,t in enumerate(tc) if t>1400 
                    for j in range(len(xv)))),
            ("BCC+FCC two-phase region exists", lambda pm, tc, xv:
                any("BCC_A2" in pm[i,j] and "FCC_A1" in pm[i,j] 
                    for i in range(len(tc)) for j in range(len(xv)))),
        ]
    },
    {
        "name": "Fe-Ti",
        "components": ["FE", "TI", "VA"],
        "phases": ["BCC_A2", "FCC_A1", "LAVES_PHASE", "LIQUID", "ETA"],
        "x_var": "TI",
        "x_label": "Mole Fraction Ti",
        "checks": [
            ("LAVES_PHASE (Fe2Ti) present", lambda pm, tc, xv:
                any("LAVES_PHASE" in pm[i,j] for i in range(len(tc)) for j in range(len(xv)))),
            ("BCC stable at low Ti", lambda pm, tc, xv:
                any("BCC_A2" in pm[i,j] for i,t in enumerate(tc) if t<800 
                    for j,x in enumerate(xv) if x<0.1)),
            ("LIQUID at high T", lambda pm, tc, xv:
                any("LIQUID" in pm[i,j] for i,t in enumerate(tc) if t>1400 
                    for j in range(len(xv)))),
        ]
    },
    {
        "name": "Fe-Mo",
        "components": ["FE", "MO", "VA"],
        "phases": ["BCC_A2", "FCC_A1", "SIGMA", "MU_PHASE", "R_PHASE", "LIQUID", "LAVES_PHASE"],
        "x_var": "MO",
        "x_label": "Mole Fraction Mo",
        "checks": [
            ("SIGMA or MU_PHASE present", lambda pm, tc, xv:
                any("SIGMA" in pm[i,j] or "MU_PHASE" in pm[i,j] 
                    for i in range(len(tc)) for j in range(len(xv)))),
            ("BCC dominant", lambda pm, tc, xv:
                any("BCC_A2" in pm[i,j] for i in range(len(tc)) for j in range(len(xv)))),
            ("LIQUID at high T", lambda pm, tc, xv:
                any("LIQUID" in pm[i,j] for i,t in enumerate(tc) if t>1400 
                    for j in range(len(xv)))),
        ]
    },
    {
        "name": "Ni-Ti",
        "components": ["NI", "TI", "VA"],
        "phases": ["BCC_A2", "FCC_A1", "ETA", "NITI2", "LAVES_PHASE", "LIQUID", "HCP_A3"],
        "x_var": "TI",
        "x_label": "Mole Fraction Ti",
        "checks": [
            ("ETA (Ni3Ti) present", lambda pm, tc, xv:
                any("ETA" in pm[i,j] for i in range(len(tc)) for j in range(len(xv)))),
            ("FCC at Ni-rich side", lambda pm, tc, xv:
                any("FCC_A1" in pm[i,j] for i,t in enumerate(tc) if t<1000 
                    for j,x in enumerate(xv) if x<0.2)),
        ]
    },
]

# ── Scan parameters ───────────────────────────────────────────────────────────
x_vals = np.linspace(0.01, 0.99, 40)
t_vals = np.arange(500, 1900, 30)  # K

# ── Run all systems ───────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
axes_flat = axes.flatten()

results_summary = []

for idx, sys in enumerate(systems):
    name = sys["name"]
    print("\n" + "=" * 60)
    print("Computing {} binary ({} phases)...".format(name, len(sys["phases"])))
    
    # Filter to phases that exist in DB
    valid_phases = [p for p in sys["phases"] if p in all_db_phases]
    missing = [p for p in sys["phases"] if p not in all_db_phases]
    if missing:
        print("  WARNING: phases not in DB: {}".format(missing))
    print("  Using phases: {}".format(valid_phases))
    
    phase_map, phase_names, t_celsius = compute_phase_map(
        db, sys["components"], valid_phases, sys["x_var"], x_vals, t_vals)
    
    print("  Active phases found: {}".format(sorted(phase_names)))
    
    # Plot
    ax = axes_flat[idx]
    plot_binary(ax, phase_map, phase_names, x_vals, t_celsius,
                sys["x_label"], name)
    
    # Run checks
    sys_results = []
    for check_name, check_fn in sys["checks"]:
        passed = check_fn(phase_map, t_celsius, x_vals)
        status = "PASS" if passed else "FAIL"
        print("  [{}] {}".format(status, check_name))
        sys_results.append((check_name, passed))
    
    results_summary.append((name, sys_results))

# Hide unused subplot
axes_flat[5].set_visible(False)

fig.suptitle(
    "mc_fe_v2062_clean.tdb — Multi-Binary Validation Suite\n"
    "MatCalc steel database (v2.062) sanitized for PyCalphad compatibility",
    fontsize=13, fontweight="bold"
)
plt.tight_layout()
plt.savefig("multi_binary_validation.png", dpi=150, bbox_inches="tight")
print("\n\nPlot saved → multi_binary_validation.png")

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)
total_pass = 0
total_fail = 0
for name, checks in results_summary:
    for check_name, passed in checks:
        symbol = "✓" if passed else "✗"
        total_pass += passed
        total_fail += (not passed)
        print("  {} {}: {}".format(symbol, name, check_name))

print("\n  Total: {}/{} checks passed".format(total_pass, total_pass + total_fail))
print("=" * 60)
