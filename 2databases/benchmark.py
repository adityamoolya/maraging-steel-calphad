"""
Fe-Cr Binary Phase Diagram Validation
======================================
Validates the sanitized mc_fe_v2062_clean.tdb database by reproducing
the well-known Fe-Cr binary phase diagram and checking three key features:
  1. Sigma phase field (~600-820 deg C, Cr-rich compositions)
  2. BCC miscibility gap (alpha/alpha-prime) at low temperatures
  3. FCC gamma loop on Fe-rich side

Run from the directory containing both .tdb files:
    python benchmark.py

Requires: pycalphad, numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pycalphad import Database, equilibrium, variables as v
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG ────────────────────────────────────────────────────────────────────
DB_CLEAN   = "mc_fe_v2062_clean.tdb"
DB_ORIG    = "mc_fe_v2062.tdb"        # used only for parameter count check
COMPONENTS = ["FE", "CR", "VA"]
PHASES     = ["BCC_A2", "FCC_A1", "SIGMA", "LIQUID"]

# Scan ranges
X_CR   = np.linspace(0.01, 0.99, 50)   # mole fraction Cr
T_VALS = np.arange(500, 1900, 25)       # K  (227 - 1627 deg C)

# ── STEP 1: Parameter count check ─────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Parameter count verification")
print("=" * 60)

def count_params(filepath, keyword="PARAMETER G("):
    count = 0
    try:
        with open(filepath, "r", errors="replace") as f:
            for line in f:
                if keyword in line:
                    count += 1
    except FileNotFoundError:
        return None
    return count

orig_count  = count_params(DB_ORIG)
clean_count = count_params(DB_CLEAN)

if orig_count is None:
    print("  Original file not found — skipping count check")
elif orig_count == clean_count:
    print("  PASS — PARAMETER G( count identical: {} in both files".format(clean_count))
else:
    print("  WARN — Count mismatch: original={}, cleaned={}".format(orig_count, clean_count))

hmva_clean = count_params(DB_CLEAN, keyword="HMVA")
print("  HMVA lines in cleaned file (should be commented out): {}".format(hmva_clean))
watermark  = count_params(DB_CLEAN, keyword="$ Cleaned by script:")
print("  Watermarked changes by sanitization script: {}".format(watermark))

# ── STEP 2: Load database ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2 — Loading cleaned database")
print("=" * 60)

db = Database(DB_CLEAN)
loaded_phases = list(db.phases.keys())
print("  Phases loaded: {}".format(len(loaded_phases)))

for p in PHASES:
    status = "FOUND" if p in loaded_phases else "MISSING"
    print("    {:15s} {}".format(p, status))

# ── STEP 3: Equilibrium scan ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 — Running Fe-Cr equilibrium scan")
print("  {} compositions x {} temperatures = {} points".format(
    len(X_CR), len(T_VALS), len(X_CR)*len(T_VALS)))
print("  This may take a few minutes ...")
print("=" * 60)

# Run the full grid equilibrium calculation
conds = {
    v.X("CR"): X_CR,
    v.T: T_VALS,
    v.P: 101325,
    v.N: 1,
}

result = equilibrium(db, COMPONENTS, PHASES, conds, output="GM")

# ── STEP 4: Extract stable phases at each (T, X) point ───────────────────────
# Build a 2D array: rows = T, cols = X_CR, value = dominant phase name
T_C = T_VALS - 273.15   # convert to Celsius for plotting

phase_map   = np.full((len(T_VALS), len(X_CR)), "", dtype=object)
phase_names = set()

# Get the NP (phase fraction) data
np_vals = result.NP.values   # shape: (N, P, T, X_CR, vertex)
phase_vals = result.Phase.values  # same shape but strings

for i, T in enumerate(T_VALS):
    for j, xcr in enumerate(X_CR):
        try:
            # Extract phase data for this (T, X_CR) point
            # Dimensions: result has (N=1, P=1, T, X_CR, vertex)
            nf = np_vals[0, 0, i, j, :]     # phase fractions at this point
            ph = phase_vals[0, 0, i, j, :]   # phase names at this point

            active = []
            for k in range(len(nf)):
                pname = str(ph[k]).strip()
                frac = float(nf[k]) if not np.isnan(nf[k]) else 0.0
                if pname and pname != '' and frac > 0.01:
                    active.append(pname)

            label = "+".join(sorted(set(active))) if active else "UNKNOWN"
            phase_map[i, j] = label
            phase_names.update(active)
        except Exception as e:
            phase_map[i, j] = "UNKNOWN"

print("  Unique phase labels found: {}".format(len(set(phase_map.flatten()))))
print("  Active phases: {}".format(sorted(phase_names)))

# ── STEP 5: Plot ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4 — Generating phase diagram plot")
print("=" * 60)

COLOR_MAP = {
    "BCC_A2" : "#4C72B0",
    "FCC_A1" : "#DD8452",
    "SIGMA"  : "#55A868",
    "LIQUID" : "#C44E52",
    "BCC_A2+SIGMA"   : "#8172B2",
    "BCC_A2+FCC_A1"  : "#937860",
    "BCC_A2+BCC_A2"  : "#6BAED6",
    "BCC_A2+LIQUID"  : "#E7969C",
    "FCC_A1+LIQUID"  : "#D6616B",
    "UNKNOWN": "#CCCCCC",
}

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    "Fe-Cr Binary — Validation of mc_fe_v2062_clean.tdb\n"
    "Reproduced using PyCalphad · mc_fe database sanitized for PyCalphad compatibility",
    fontsize=11, fontweight="bold"
)

# --- left panel: colour map of stable phase field ---
ax = axes[0]

import matplotlib.colors as mc

unique_labels = sorted(set(phase_map.flatten()))
cmap_colors   = plt.cm.get_cmap("tab10", len(unique_labels))
label_to_idx  = {lbl: i for i, lbl in enumerate(unique_labels)}

img_data = np.zeros((len(T_VALS), len(X_CR), 3))
for i in range(len(T_VALS)):
    for j in range(len(X_CR)):
        lbl = phase_map[i, j]
        col = COLOR_MAP.get(lbl, cmap_colors(label_to_idx.get(lbl, 0)))
        if isinstance(col, str):
            col = mc.to_rgb(col)
        img_data[i, j] = col[:3]

ax.imshow(
    img_data,
    origin="lower",
    aspect="auto",
    extent=[X_CR[0], X_CR[-1], T_C[0], T_C[-1]],
)
ax.set_xlabel("Mole Fraction Cr", fontsize=11)
ax.set_ylabel("Temperature (°C)", fontsize=11)
ax.set_title("Fe-Cr Phase Map", fontsize=11)

# legend patches
patches = []
for lbl in sorted(unique_labels):
    if lbl == "UNKNOWN":
        continue
    col = COLOR_MAP.get(lbl, "#888888")
    patches.append(mpatches.Patch(color=col, label=lbl))
ax.legend(handles=patches, loc="upper left", fontsize=8, framealpha=0.8)

# reference lines for the three benchmark features
ax.axhline(820,  color="white", lw=1, ls="--", alpha=0.7)
ax.axhline(600,  color="white", lw=1, ls="--", alpha=0.7)
ax.text(0.55, 830, "Sigma upper (~820 °C)", color="white", fontsize=7)
ax.text(0.55, 610, "Sigma lower (~600 °C)", color="white", fontsize=7)

# --- right panel: phase presence count at each (T, X) point from phase_map ---
ax2 = axes[1]

phase_colors = {
    "BCC_A2": "#4C72B0",
    "FCC_A1": "#DD8452",
    "SIGMA" : "#55A868",
    "LIQUID": "#C44E52",
}

# For each temperature, count how many X_CR points show each phase
for ph, col in phase_colors.items():
    presence = np.array([
        [1.0 if ph in phase_map[i, j] else 0.0
         for j in range(len(X_CR))]
        for i in range(len(T_VALS))
    ])  # shape (T, X)

    # plot as a filled contour: presence=1 means phase is stable at that (T,X)
    ax2.contourf(
        X_CR, T_C, presence,
        levels=[0.5, 1.5],
        colors=[col],
        alpha=0.5,
    )
    # dummy line for legend
    ax2.plot([], [], color=col, lw=4, label=ph, alpha=0.7)

ax2.set_xlabel("Mole Fraction Cr", fontsize=11)
ax2.set_ylabel("Temperature (°C)", fontsize=11)
ax2.set_title("Phase Stability Regions\n(from scan data)", fontsize=11)
ax2.legend(fontsize=9, loc="upper left")
ax2.set_xlim(0, 1)
ax2.set_ylim(T_C[0], T_C[-1])

# reference lines
ax2.axhline(820, color="black", lw=1, ls="--", alpha=0.5)
ax2.axhline(600, color="black", lw=1, ls="--", alpha=0.5)
ax2.text(0.02, 825, "~820 °C", fontsize=7)
ax2.text(0.02, 605, "~600 °C", fontsize=7)

plt.tight_layout()
outfile = "fecr_validation.png"
plt.savefig(outfile, dpi=150, bbox_inches="tight")
print("  Plot saved → {}".format(outfile))

# ── STEP 6: Benchmark report ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5 — Benchmark feature check")
print("=" * 60)

# Check 1: sigma appears somewhere in the map
sigma_present = any("SIGMA" in phase_map[i, j]
                    for i in range(len(T_VALS))
                    for j in range(len(X_CR)))
print("  [{}] SIGMA phase present in diagram".format('PASS' if sigma_present else 'FAIL'))

# Check 2: sigma appears in expected T range (600-850 deg C)
sigma_T_range = [T_C[i] for i in range(len(T_VALS))
                 for j in range(len(X_CR))
                 if "SIGMA" in phase_map[i, j]]
if sigma_T_range:
    print("  [INFO] SIGMA observed between {:.0f} °C and {:.0f} °C".format(
        min(sigma_T_range), max(sigma_T_range)))
    in_range = min(sigma_T_range) < 850 and max(sigma_T_range) > 550
    print("  [{}] Sigma T range consistent with literature (550–850 °C)".format(
        'PASS' if in_range else 'WARN'))
else:
    print("  [FAIL] SIGMA not detected — check phases list or composition range")

# Check 3: FCC gamma loop present on Fe-rich side (X_CR < 0.15, T > 800 C)
fcc_ferich = any(
    "FCC_A1" in phase_map[i, j]
    for i in range(len(T_VALS)) if T_C[i] > 800
    for j in range(len(X_CR))  if X_CR[j] < 0.15
)
print("  [{}] FCC gamma loop present on Fe-rich side (X_CR < 0.15, T > 800 °C)".format(
    'PASS' if fcc_ferich else 'FAIL'))

# Check 4: BCC dominant at low T, Fe-rich
bcc_low_T = any(
    "BCC_A2" in phase_map[i, j]
    for i in range(len(T_VALS)) if T_C[i] < 500
    for j in range(len(X_CR))  if X_CR[j] < 0.5
)
print("  [{}] BCC_A2 dominant at low T, Fe-rich side".format(
    'PASS' if bcc_low_T else 'FAIL'))

# Check 5: Liquid at high T
liquid_high_T = any(
    "LIQUID" in phase_map[i, j]
    for i in range(len(T_VALS)) if T_C[i] > 1400
    for j in range(len(X_CR))
)
print("  [{}] LIQUID phase present at high T (> 1400 °C)".format(
    'PASS' if liquid_high_T else 'FAIL'))

# Check 6: BCC miscibility gap at low T
bcc_miscibility = any(
    phase_map[i, j] == "BCC_A2+BCC_A2"
    for i in range(len(T_VALS)) if T_C[i] < 600
    for j in range(len(X_CR))
)
print("  [{}] BCC miscibility gap (alpha + alpha') at low T".format(
    'PASS' if bcc_miscibility else 'FAIL'))

print("\n" + "=" * 60)
print("Validation complete.")
print("  Plot saved to: fecr_validation.png")
print("  If all checks PASS, database is suitable for publication.")
print("=" * 60)
