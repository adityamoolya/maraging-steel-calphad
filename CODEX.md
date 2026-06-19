# Codex Project Context

## Situation

The professor asked to replicate the results from:

- `literature_validation/main_paper.pdf`
- Title: "Evolution and strengthening of nanoprecipitates in a high strength maraging stainless steel"
- Li et al., Materials Science & Engineering A, 2024

By mistake, much of the current README/project framing follows:

- `literature_validation/structel.pdf`
- Title: "Heterogeneous nucleation of Ni3Ti by Mo-enriched particles enhances strength and fracture toughness of maraging steel"
- Xu et al., Journal of Materials Research and Technology, 2025

These papers are scientifically related, but they are not the same target. The existing work is not useless, but the writeup and next deliverables need to pivot to `main_paper.pdf`.

## Current Repo State

Current useful work:

- `README.md` currently frames the project around Xu et al. 2025 / DAT aging.
- CALPHAD/PyCalphad setup exists in `notebooks/1.setup.ipynb`, `notebooks/2.equilibrium.ipynb`, and related scripts.
- Cleaned thermodynamic database exists at `2databases/mc_fe_v2062_clean.tdb`.
- DFT outputs exist for eta-Ni3Ti and pure elements in `dft/`.
- Existing DFT result for eta-Ni3Ti formation energy is useful as supporting evidence for Ni3Ti stability.
- Some attempted clustered/dispersed DFT input/output files exist:
  - `dft/fe54_3ni_clustered.*`
  - `dft/fe54_3ni_dispersed.*`
  - `dft/fe54_5mo_clustered.*`
  - `dft/fe54_5mo_dispersed.*`

Important limitation:

- The clustered/dispersed DFT supercell calculations did not converge well on local laptop hardware. A reduced 54-56 atom BCC model still took hours and did not fully complete. Do not make full Fig. 8c DFT replication the main claim unless proper compute is available.

## Assigned Paper: Key Results To Replicate

The assigned paper, Li et al. 2024, has mostly experimental results that cannot be genuinely reproduced without lab equipment:

- Hardness evolution vs aging time, Fig. 1a
- Stress-strain curves, Fig. 1b
- EBSD grain/phase maps, Fig. 2
- TEM/HRTEM precipitate images, Figs. 3-5
- APT atom distribution maps, Figs. 6-7

Computationally useful/reproducible parts:

- Section 4.1 / Fig. 8c: clustered vs dispersed first-principles formation energies for Ni, Mo, Cr in Fe-Co-X supercells.
- Section 4.2 / Fig. 9 / Table 4: analytical strengthening model and predicted yield strength contributions.

Given current hardware/time, the strongest recovery path is Section 4.2, not full DFT.

## Main Paper Composition And Heat Treatment

Target composition from `main_paper.pdf`:

- Fe-11Cr-4Co-8Ni-0.5Ti-5Mo-0.1Si-0.002C wt.%

Target aging treatment:

- Aging at 480 deg C for different times.
- Important labels:
  - `SA30`: 30 min
  - `SA300`: 300 min
  - `SA3000`: 3000 min
  - `SA30000`: 30000 min

Do not frame the primary replication around DAT `370 deg C + 480 deg C`; that belongs to Xu et al. 2025.

## Main Paper Conclusions To Match

Core precipitation sequence:

```text
Ni-rich cluster
-> Ni-rich cluster + Mo-rich cluster
-> Ni3Ti + Mo-rich phase
-> Ni3Ti + Mo-rich phase + alpha'-Cr
```

Mechanical properties reported:

- Yield strength: about 1750 MPa
- Tensile strength: about 1910 MPa
- Total elongation: about 10.5%

Important interpretation:

- Ni-rich and Mo-rich clusters are early-stage strengthening precipitates.
- Ni-rich clusters evolve toward Ni3Ti.
- Mo-rich phases wrap/inhibit Ni3Ti coarsening.
- alpha'-Cr appears late.
- Reverted austenite improves ductility by TRIP effect.
- Ordered strengthening dominates shearing contributions.
- Mo-rich phase eventually coarsens enough that Orowan bypass dominates.

## Table 1 Data From Main Paper

Use these as manual inputs for strengthening-model replication. Units:

- Equivalent radius: nm
- Number density: 10^23 m^-3
- Volume fraction: %

```text
SA30:
  Ni-rich cluster:
    radius = 0.95 +/- 0.31
    number_density = 60.56 +/- 0.98
    volume_fraction = 3.12 +/- 0.91

SA300:
  Ni-rich cluster:
    radius = 1.11 +/- 0.53
    number_density = 50.12 +/- 0.97
    volume_fraction = 3.81 +/- 1.11
  Mo-rich cluster:
    radius = 1.47 +/- 2.15
    number_density = 2.01 +/- 0.12
    volume_fraction = 2.57 +/- 1.51

SA3000:
  Ni3Ti:
    radius = 3.43 +/- 1.86
    number_density = 4.71 +/- 0.89
    volume_fraction = 4.37 +/- 0.73
  Mo-rich phase:
    radius = 6.81 +/- 1.93
    number_density = 0.71 +/- 0.47
    volume_fraction = 8.56 +/- 1.13

SA30000:
  Ni3Ti:
    radius = 3.89 +/- 1.91
    number_density = 5.13 +/- 1.27
    volume_fraction = 5.46 +/- 1.21
  Mo-rich phase:
    radius = 8.02 +/- 2.45
    number_density = 0.53 +/- 0.27
    volume_fraction = 11.63 +/- 2.27
  alpha'-Cr:
    radius appears in conclusion as 1.53 nm
```

## Target Strengthening Values

The paper reports approximate precipitation strengthening increments:

```text
SA30:    545 MPa
SA300:   727 MPa
SA3000:  925 MPa
SA30000: 1175 MPa
```

The recovery deliverable should reproduce these values or a close version using the paper's equations and table values.

Critical radii from the paper:

```text
Ni3Ti:        5.37 nm
Mo-rich:      6.52 nm
alpha'-Cr:    5.94 nm
```

Mechanism interpretation:

- Ni-rich clusters and Ni3Ti: shearing/order strengthening.
- Mo-rich clusters: shearing when small.
- Mo-rich phase: Orowan bypass when radius exceeds critical radius.
- alpha'-Cr: shearing/order strengthening.

## Recommended Next Steps

1. Create a new notebook or script:
   - Suggested: `notebooks/4.main_paper_strengthening.ipynb`
   - Alternative script: `scripts/main_paper_strengthening.py`

2. Manually input Table 1 precipitate data from `main_paper.pdf`.

3. Implement/reproduce Section 4.2 strengthening model:
   - Orowan bypass for coarsened Mo-rich phase.
   - Shearing/order strengthening for Ni-rich clusters, Ni3Ti, and alpha'-Cr.
   - Recreate a Table 4-like output.
   - Recreate a Fig. 9-like bar chart showing strengthening contributions.

4. Update `README.md`:
   - Make Li et al. 2024 / `main_paper.pdf` the primary target.
   - Move Xu et al. 2025 / `structel.pdf` to related/secondary validation.
   - State that experimental microscopy/tensile data are not physically reproduced, only digitized/extracted and modeled.
   - State that full Fig. 8c DFT was attempted but is limited by local compute; use converged Ni3Ti formation energy as supporting evidence only.

5. Optional if time permits:
   - Add CALPHAD calculation at the assigned composition and 480 deg C.
   - Show qualitative phase tendency for Ni3Ti/Mo-rich/Cr-rich precipitates.
   - Do not claim CALPHAD reproduces aging kinetics.

## Suggested Scope Statement

Use this wording or similar:

```text
This project computationally reproduces the precipitation-strengthening trends reported by Li et al. (2024) using extracted precipitate statistics, analytical strengthening equations, CALPHAD thermodynamic support, and limited DFT validation of Ni3Ti stability. Full experimental characterization and large-supercell clustered/dispersed DFT calculations are outside the scope of the available lab and local computing resources.
```

