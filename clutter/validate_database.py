"""
Validate mc_fe_v2062_clean.tdb using pycalphad.

Tests performed:
  1. Database loading & element/phase inventory
  2. Single-point equilibrium for a maraging steel composition (Fe-18Ni-9Co-5Mo-0.7Ti-0.1Al wt%)
  3. Phase fraction vs temperature (property diagram) — saved as PNG
  4. Binary Ni-Ti section sanity check — saved as PNG
"""

import os
import sys
import warnings
import numpy as np

warnings.filterwarnings("ignore")

# ── pycalphad imports ──────────────────────────────────────────────────
from pycalphad import Database, equilibrium, variables as v

# ── paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
TDB_PATH = os.path.join(PROJECT_DIR, "2databases", "mc_fe_v2062_clean.tdb")
FIG_DIR = os.path.join(PROJECT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ======================================================================
# 1. Load database & print inventory
# ======================================================================
print("=" * 70)
print("1. LOADING DATABASE")
print("=" * 70)
try:
    db = Database(TDB_PATH)
    print(f"   ✓ Database loaded: {os.path.basename(TDB_PATH)}")
except Exception as e:
    print(f"   ✗ FAILED to load database: {e}")
    sys.exit(1)

elements = sorted(db.elements - {"/-"})
phases = sorted(db.phases.keys())
print(f"   Elements ({len(elements)}): {', '.join(elements)}")
print(f"   Phases   ({len(phases)}): {', '.join(phases)}")

# ======================================================================
# 2. Single-point equilibrium — maraging steel at 750 K (aging temp)
# ======================================================================
print("\n" + "=" * 70)
print("2. SINGLE-POINT EQUILIBRIUM — Maraging steel @ 750 K")
print("=" * 70)

# Typical 18Ni maraging steel (wt%): Fe-18Ni-9Co-5Mo-0.7Ti-0.1Al
# Convert to mole fractions (approximate)
# We'll just use equilibrium() directly

COMPONENTS = ["FE", "NI", "CO", "MO", "TI", "AL", "VA"]
# Phases relevant to maraging steel
PHASES_MARAGING = [
    "LIQUID", "FCC_A1", "BCC_A2", "HCP_A3",
    "ETA",           # Ni3Ti — main strengthening precipitate
    "NITI2",         # NiTi2
    "LAVES_PHASE",   # Fe2Mo type
    "MU_PHASE",      # Fe7Mo6
    "SIGMA",
    "GAMMA_PRIME",   # Ni3(Ti,Al) — ordered L12
]

# Filter to only phases that exist in this database
available_phases = [p for p in PHASES_MARAGING if p in db.phases]
print(f"   Available phases: {available_phases}")
missing = [p for p in PHASES_MARAGING if p not in db.phases]
if missing:
    print(f"   Missing phases (skipped): {missing}")

# Mole fractions for Fe-18Ni-9Co-5Mo-0.7Ti-0.1Al (wt%)
# Approximate mole fractions:
#   Fe ~0.6513, Ni ~0.1724, Co ~0.0859, Mo ~0.0293, Ti ~0.0082, Al ~0.0021
conditions = {
    v.T: 750,
    v.P: 101325,
    v.N: 1,
    v.X("NI"): 0.1724,
    v.X("CO"): 0.0859,
    v.X("MO"): 0.0293,
    v.X("TI"): 0.0082,
    v.X("AL"): 0.0021,
}

print(f"\n   Conditions:")
print(f"     T = 750 K  (≈ 477 °C, typical aging temperature)")
print(f"     P = 101325 Pa")
print(f"     x(Ni) = 0.1724, x(Co) = 0.0859, x(Mo) = 0.0293")
print(f"     x(Ti) = 0.0082, x(Al) = 0.0021, x(Fe) = balance")
print(f"\n   Computing equilibrium...")

try:
    eq_result = equilibrium(
        db,
        COMPONENTS,
        available_phases,
        conditions,
    )

    # Extract phase fractions
    print(f"\n   ✓ Equilibrium converged!")
    print(f"\n   Phase fractions (NP):")
    
    phase_names = eq_result.Phase.values.squeeze()
    phase_fracs = eq_result.NP.values.squeeze()
    
    for name, frac in zip(phase_names, phase_fracs):
        if name == "" or name == "":
            continue
        if np.isnan(frac) or frac < 1e-8:
            continue
        print(f"     {name:20s}  NP = {frac:.6f}")

    # Physical checks
    print(f"\n   Sanity checks:")
    total_np = np.nansum(phase_fracs)
    print(f"     Sum of phase fractions = {total_np:.6f}  (should be ≈ 1.0)")
    
    # Check that BCC_A2 or FCC_A1 is the matrix
    stable_phases = [n for n, f in zip(phase_names, phase_fracs) 
                     if isinstance(n, str) and n.strip() and not np.isnan(f) and f > 0.01]
    has_matrix = any(p in stable_phases for p in ["BCC_A2", "FCC_A1"])
    print(f"     Matrix phase present (BCC or FCC): {'✓ Yes' if has_matrix else '✗ No — SUSPICIOUS'}")
    
    has_precipitate = any(p in stable_phases for p in ["ETA", "GAMMA_PRIME", "LAVES_PHASE", "NITI2"])
    print(f"     Precipitate phase present: {'✓ Yes' if has_precipitate else '✗ No — Check aging T'}")

except Exception as e:
    print(f"   ✗ Equilibrium FAILED: {e}")
    import traceback
    traceback.print_exc()

# ======================================================================
# 3. Phase fraction vs temperature (property diagram)
# ======================================================================
print("\n" + "=" * 70)
print("3. PROPERTY DIAGRAM — Phase fraction vs T (673–1800 K)")
print("=" * 70)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T_range = np.arange(673, 1801, 25)
print(f"   Computing equilibria at {len(T_range)} temperatures...")
print(f"   T range: {T_range[0]} – {T_range[-1]} K, step = 25 K")

conditions_step = {
    v.T: T_range,
    v.P: 101325,
    v.N: 1,
    v.X("NI"): 0.1724,
    v.X("CO"): 0.0859,
    v.X("MO"): 0.0293,
    v.X("TI"): 0.0082,
    v.X("AL"): 0.0021,
}

try:
    eq_step = equilibrium(
        db,
        COMPONENTS,
        available_phases,
        conditions_step,
    )
    print("   ✓ Step calculation complete!")

    # Extract & plot
    fig, ax = plt.subplots(figsize=(10, 6))

    phase_data = {}
    T_vals = eq_step.T.values.squeeze()
    all_phase_names = eq_step.Phase.values.squeeze()
    all_phase_fracs = eq_step.NP.values.squeeze()

    # Collect phase fractions across T
    for i, T_val in enumerate(T_vals):
        names = all_phase_names[i] if all_phase_names.ndim > 1 else all_phase_names
        fracs = all_phase_fracs[i] if all_phase_fracs.ndim > 1 else all_phase_fracs
        for name, frac in zip(names, fracs):
            if not isinstance(name, str) or name.strip() == "":
                continue
            if np.isnan(frac):
                continue
            if name not in phase_data:
                phase_data[name] = {"T": [], "NP": []}
            phase_data[name]["T"].append(T_val)
            phase_data[name]["NP"].append(frac)

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(phase_data), 1)))
    for idx, (phase_name, data) in enumerate(sorted(phase_data.items())):
        ax.plot(data["T"], data["NP"], "o-", label=phase_name,
                color=colors[idx % len(colors)], markersize=3, linewidth=1.5)

    ax.set_xlabel("Temperature (K)", fontsize=12)
    ax.set_ylabel("Phase fraction (NP)", fontsize=12)
    ax.set_title("Fe-18Ni-9Co-5Mo-0.7Ti-0.1Al — Phase Fractions vs T\n"
                 f"Database: mc_fe_v2062_clean.tdb", fontsize=13)
    ax.legend(loc="best", fontsize=9)
    ax.set_xlim(673, 1800)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_path = os.path.join(FIG_DIR, "maraging_phase_fraction_vs_T.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"   ✓ Plot saved: {out_path}")

except Exception as e:
    print(f"   ✗ Step calculation FAILED: {e}")
    import traceback
    traceback.print_exc()

# ======================================================================
# 4. Binary Ni-Ti check (Fe=0, just Ni-Ti, x(Ti) sweep at 1000 K)
# ======================================================================
print("\n" + "=" * 70)
print("4. BINARY CHECK — Ni-Ti phase fractions at 1000 K")
print("=" * 70)

COMPONENTS_BINARY = ["NI", "TI", "VA"]
PHASES_BINARY = ["LIQUID", "FCC_A1", "BCC_A2", "HCP_A3", "ETA", "NITI2"]
available_binary = [p for p in PHASES_BINARY if p in db.phases]

x_ti_range = np.linspace(0.01, 0.99, 50)
print(f"   Computing Ni-Ti equilibria at 50 compositions, T = 1000 K...")

try:
    eq_binary = equilibrium(
        db,
        COMPONENTS_BINARY,
        available_binary,
        {v.T: 1000, v.P: 101325, v.N: 1, v.X("TI"): x_ti_range},
    )
    print("   ✓ Binary calculation complete!")

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    phase_data2 = {}
    xti_vals = eq_binary.X.sel(component="TI").values.squeeze()
    # Actually let's use the condition values
    all_phase_names2 = eq_binary.Phase.values.squeeze()
    all_phase_fracs2 = eq_binary.NP.values.squeeze()

    for i, xti in enumerate(x_ti_range):
        names = all_phase_names2[i] if all_phase_names2.ndim > 1 else all_phase_names2
        fracs = all_phase_fracs2[i] if all_phase_fracs2.ndim > 1 else all_phase_fracs2
        for name, frac in zip(names, fracs):
            if not isinstance(name, str) or name.strip() == "":
                continue
            if np.isnan(frac):
                continue
            if name not in phase_data2:
                phase_data2[name] = {"x": [], "NP": []}
            phase_data2[name]["x"].append(xti)
            phase_data2[name]["NP"].append(frac)

    colors2 = plt.cm.Set1(np.linspace(0, 1, max(len(phase_data2), 1)))
    for idx, (phase_name, data) in enumerate(sorted(phase_data2.items())):
        ax2.plot(data["x"], data["NP"], "o-", label=phase_name,
                 color=colors2[idx % len(colors2)], markersize=3, linewidth=1.5)

    ax2.set_xlabel("x(Ti)", fontsize=12)
    ax2.set_ylabel("Phase fraction (NP)", fontsize=12)
    ax2.set_title("Ni-Ti binary — Phase fractions vs x(Ti) at 1000 K\n"
                  f"Database: mc_fe_v2062_clean.tdb", fontsize=13)
    ax2.legend(loc="best", fontsize=9)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.02, 1.05)
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()

    out_path2 = os.path.join(FIG_DIR, "niti_binary_1000K.png")
    fig2.savefig(out_path2, dpi=150)
    plt.close(fig2)
    print(f"   ✓ Plot saved: {out_path2}")

except Exception as e:
    print(f"   ✗ Binary calculation FAILED: {e}")
    import traceback
    traceback.print_exc()

# ======================================================================
# Summary
# ======================================================================
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print(f"   Database: {os.path.basename(TDB_PATH)}")
print(f"   Elements: {len(elements)}")
print(f"   Phases:   {len(phases)}")
print(f"   Figures saved to: {FIG_DIR}/")
print("=" * 70)
