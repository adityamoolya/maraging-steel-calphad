# Computational Replication of Li et al. 2024 Maraging Steel Precipitation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Paper Being Replicated](#paper-being-replicated)
3. [Main Scientific Questions](#main-scientific-questions)
4. [Methods and Files](#methods-and-files)
5. [Notebook Results](#notebook-results)
6. [DFT Simulations on VPS](#dft-simulations-on-vps)
7. [Figures](#figures)
8. [What We Replicated](#what-we-replicated)
9. [Limitations](#limitations)
10. [How to Reproduce](#how-to-reproduce)
11. [Repository Structure](#repository-structure)

## Project Overview

This repository studies the precipitation behavior and strengthening mechanism reported by Li et al. 2024 for a high strength maraging stainless steel aged at 480 °C. The aim is not to reproduce the experimental microscopy itself, but to computationally test the paper's main interpretation using:

* CALPHAD equilibrium calculations for the reported alloy composition.
* Analytical precipitate strengthening equations from Section 4.2 of the paper.
* Quantum ESPRESSO DFT calculations comparing clustered and dispersed Ni/Mo solute configurations in BCC Fe supercells.

The work is intended as a compact professor-facing explanation of what we reproduced, what agrees with the paper, and where the current model is still incomplete.

## Paper Being Replicated

**Target paper:** Li et al., "Evolution and strengthening of nanoprecipitates in a high strength maraging stainless steel," Materials Science & Engineering A 915 (2024) 147198.

**Local text/PDF:**  
* [`literature_validation/main_paper.txt`](./literature_validation/main_paper.txt)
* [`literature_validation/main_paper.pdf`](./literature_validation/main_paper.pdf)

**Alloy composition from the paper:**  
Fe-11.0Cr-4.0Co-8.0Ni-0.5Ti-5.0Mo-0.1Si-0.002C wt.%

**Aging condition emphasized here:**  
480 °C, especially the SA30000 condition used for long-time precipitate analysis.

## Main Scientific Questions

The paper asks several linked questions about this alloy:

1. What precipitation sequence occurs during aging at 480 °C?
2. Why do Ni-rich clusters appear first, followed by Mo-rich clusters, Ni3Ti, Mo-rich phase, and finally alpha-prime Cr?
3. Which precipitates provide the main yield strength increment?
4. Is the dominant strengthening mechanism particle shearing or Orowan bypassing?
5. Why is ordered strengthening the largest part of the shearing contribution?
6. How do reverted austenite and nanoprecipitates together allow high strength while preserving ductility?

Our notebooks directly address questions 1, 2, 3, and 4 in a computational way. We do not reproduce the EBSD, XRD, TEM, HRTEM, APT, tensile testing, or RA/TRIP analysis experimentally.

## Methods and Files

### 1. CALPHAD Equilibrium

Notebook:
* [`notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb`](./notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb)

Script version:
* [`notebooks/li_et_al_2024/1.calphad_equilibrium.py`](./notebooks/li_et_al_2024/1.calphad_equilibrium.py)

Database:
* [`2databases/mc_fe_v2062_clean.tdb`](./2databases/mc_fe_v2062_clean.tdb)

Purpose:
* Convert the paper's wt.% composition to mole fractions.
* Run PyCalphad equilibrium calculations from 300 °C to 1100 °C.
* Run an isothermal equilibrium calculation at 480 °C.
* Check whether the thermodynamic endpoint contains the same phase families reported by Li et al.: BCC matrix, Ni3Ti, Mo-rich phase, and Cr-related phase.

### 2. Strengthening Model

Notebook:
* [`notebooks/li_et_al_2024/2.strength_model.ipynb`](./notebooks/li_et_al_2024/2.strength_model.ipynb)

Script version:
* [`notebooks/li_et_al_2024/2.strength_model.py`](./notebooks/li_et_al_2024/2.strength_model.py)

Purpose:
* Implement the paper's Section 4.2 analytical strengthening equations for Ni3Ti.
* Compare calculated coherency, modulus mismatch, and order strengthening against the paper-reported values for SA30000.
* Compare total shearing stress with Orowan bypassing stress.

Equations used from the paper:

```text
Yield strength:
sigma_Y = sigma_Mart + sigma_ss + sigma_p

Martensite contribution:
sigma_Mart = 300 / sqrt(d_block) + 0.25 M mu b sqrt(rho)

Solid solution contribution:
sigma_ss = sum_i(beta_i^2 x_i,alpha)^0.5

Coherency strengthening:
Delta sigma_coherency = 4.1 M G epsilon^(3/2) f^(1/2) (r / b)^(1/2)

Modulus mismatch strengthening:
Delta sigma_modulus = 0.0055 M (Delta G)^(3/2) (2f / G)^(1/2) (r / b)^(3m/2 - 1)

Order strengthening:
Delta sigma_order = M (gamma_apb / 2b) (3 pi f / 8)^(1/2)

Total shearing:
Delta sigma_shearing = Delta sigma_coherency + Delta sigma_modulus + Delta sigma_order

Orowan bypassing:
Delta sigma_Orowan = M (0.4 G b) / (pi sqrt(1 - nu)) * ln(2 r_s / b) / L

Interparticle spacing:
L = 2 r_s (pi / 4f - 1)^(1/2)

Multiple precipitate superposition:
sigma_p = (sum_j Delta sigma_j^2)^0.5
```

Constants used in the notebook:

```text
M = 2.5
b = 0.28 nm
G = 71 GPa
nu = 0.3
f = 0.0546
d_p = 3.6 nm
r = 1.8 nm
r_s = sqrt(2/3) r
G_p = 55 GPa for Ni3Ti
Delta G = 16 GPa
gamma_apb = 0.52 J/m^2
m = 0.85
epsilon = 0.00527, back-calculated from the paper's coherency value
```

### 3. DFT Clustered vs Dispersed Solute Comparison

Notebook:
* [`notebooks/li_et_al_2024/3.dft_clustering.ipynb`](./notebooks/li_et_al_2024/3.dft_clustering.ipynb)

DFT input review:
* [`dft/vps/correction.md`](./dft/vps/correction.md)

Purpose:
* Compare total energies of clustered and dispersed solute configurations in a 54-atom BCC Fe supercell.
* Compute Delta E = E_clustered - E_dispersed.
* Convert Ry to meV using 1 Ry = 13605.7 meV.
* Interpret positive Delta E as dispersed being lower in energy.

## Notebook Results

### CALPHAD Findings

From [`1.calphad_equilibrium.ipynb`](./notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb):

Composition conversion:

| Element | wt.% | mole fraction |
| --- | ---: | ---: |
| Fe | 71.398 | 0.72621 |
| Cr | 11.000 | 0.12017 |
| Ni | 8.000 | 0.07742 |
| Mo | 5.000 | 0.02960 |
| Co | 4.000 | 0.03855 |
| Ti | 0.500 | 0.00593 |
| Si | 0.100 | 0.00202 |
| C | 0.002 | 0.00009 |

Key equilibrium phase fractions:

| Temperature | ETA/Ni3Ti | LAVES/Mo-rich | SIGMA/Cr-related |
| --- | ---: | ---: | ---: |
| 480 °C | 0.0231 | 0.0320 | 0.0871 |
| 600 °C | 0.0162 | 0.0434 | 0.0000 |
| 800 °C | 0.0000 | 0.0234 | 0.0000 |

480 °C isothermal equilibrium:

| Phase | CALPHAD mole fraction | CALPHAD mole % | Li et al. observation |
| --- | ---: | ---: | --- |
| BCC_A2 | 0.8576 | 85.76% | Dominant martensite matrix |
| SIGMA | 0.0871 | 8.71% | Cr-related phase appears at SA30000 |
| LAVES_PHASE | 0.0320 | 3.20% | Mo-rich phase observed |
| ETA | 0.0231 | 2.31% | Ni3Ti observed, about 5.46 vol.% at SA30000 |
| FCC_A1 | 0.0002 | 0.02% | Paper reports reverted austenite at long aging |

Main CALPHAD conclusion:

* The phase identities are qualitatively consistent with the paper's long-aging endpoint.
* The quantitative fractions do not match APT exactly because CALPHAD gives infinite-time equilibrium mole fractions, while Li et al. report finite-time experimental volume fractions.
* The largest mismatch is reverted austenite: the paper reports about 17.5% at SA30000, while the equilibrium calculation gives only 0.02 mol.% FCC_A1.

### Strengthening Findings

From [`2.strength_model.ipynb`](./notebooks/li_et_al_2024/2.strength_model.ipynb):

| Contribution | Notebook calculation | Paper value |
| --- | ---: | ---: |
| Coherency strengthening | 164.9 MPa | 163 MPa |
| Modulus mismatch strengthening | 57.6 MPa | 91 MPa |
| Order strengthening | 588.8 MPa | 1061 MPa |
| Total shearing | 811.3 MPa | Mechanism agrees |
| Orowan bypassing | 1653.6 MPa | Used for mechanism comparison |

Main strengthening conclusion:

* The coherency term is reproduced closely.
* The modulus and order terms are lower than the paper values.
* The mechanism conclusion still matches the paper: shearing stress is lower than Orowan bypassing stress, so Ni3Ti is predicted to strengthen mainly by particle shearing.
* The paper states that ordered strengthening is the dominant contribution. The notebook also shows order strengthening is the largest of the three shearing terms.

### DFT Clustering Findings

From [`3.dft_clustering.ipynb`](./notebooks/li_et_al_2024/3.dft_clustering.ipynb), using the converged outputs in [`dft/vps/output_vm1`](./dft/vps/output_vm1):

| System | Delta E in Ry | Delta E in meV | Interpretation |
| --- | ---: | ---: | --- |
| 3 Ni in Fe54 | +0.01188 | +161.6 | Dispersed lower in energy |
| 5 Mo in Fe54 | +0.08416 | +1145.1 | Dispersed lower in energy |

Main DFT conclusion:

* For both Ni and Mo in our fixed-cell Fe54 models, clustered configurations are higher in energy than dispersed configurations.
* This means clustering is not favored as a simple 0 K equilibrium total-energy preference in these simplified cells.
* The result supports a kinetic interpretation: clustering during aging at 480 °C requires thermal activation and local diffusion, consistent with the paper's precipitation sequence argument.

## DFT Simulations on VPS

The DFT calculations in [`dft/vps`](./dft/vps) were run on an Azure VPS with:

```text
4 vCPU
32 GB RAM
Quantum ESPRESSO
Fixed-cell SCF calculations
```

Azure worked for these fixed-cell SCF runs. For future repeat runs, AWS EC2 is recommended because it is easier to choose compute-optimized instances and scale CPU/RAM cleanly.

### DFT Input Files

| Model | Input file | Purpose |
| --- | --- | --- |
| Pure Fe54 | [`fe54_pure.scf.in`](./dft/vps/fe54_pure.scf.in) | Same-cell BCC Fe reference |
| Fe54 with 3 Ni clustered | [`fe54_3ni_clustered.scf.in`](./dft/vps/fe54_3ni_clustered.scf.in) | Clustered Ni comparison |
| Fe54 with 3 Ni dispersed | [`fe54_3ni_dispersed.scf.in`](./dft/vps/fe54_3ni_dispersed.scf.in) | Dispersed Ni comparison |
| Fe54 with 5 Mo clustered | [`fe54_5mo_clustered.scf.in`](./dft/vps/fe54_5mo_clustered.scf.in) | Clustered Mo comparison |
| Fe54 with 5 Mo dispersed | [`fe54_5mo_dispersed.scf.in`](./dft/vps/fe54_5mo_dispersed.scf.in) | Dispersed Mo comparison |

### DFT Output Files from `output_vm1`

| Output file | Final total energy (Ry) | SCF iterations | Status |
| --- | ---: | ---: | --- |
| [`fe54_pure.scf.out`](./dft/vps/output_vm1/fe54_pure.scf.out) | -13379.23285118 | 16 | Converged, JOB DONE |
| [`fe54_3ni_clustered.scf.out`](./dft/vps/output_vm1/fe54_3ni_clustered.scf.out) | -13654.31167097 | 72 | Converged, JOB DONE |
| [`fe54_3ni_dispersed.scf.out`](./dft/vps/output_vm1/fe54_3ni_dispersed.scf.out) | -13654.32354913 | 175 | Converged, JOB DONE |
| [`fe54_5mo_clustered.scf.out`](./dft/vps/output_vm1/fe54_5mo_clustered.scf.out) | -12837.86584135 | 22 | Converged, JOB DONE |
| [`fe54_5mo_dispersed.scf.out`](./dft/vps/output_vm1/fe54_5mo_dispersed.scf.out) | -12837.95000173 | 22 | Converged, JOB DONE |

Important scientific caution:

* These are fixed-cell SCF comparisons, not fully relaxed formation-energy calculations.
* The current VPS DFT set covers Ni and Mo only.
* The paper's DFT discussion uses Fe-Co-X systems and also considers Cr. Our DFT work is therefore a partial analogue of the paper's Fig. 8/Table 2, not a full replication.

## Figures

### Figures Generated by `notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb`

Figure 1:

![CALPHAD phase fraction vs temperature](./figures/fig1_phase_fraction_vs_T.png)

Generated by:
* [`notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb`](./notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb)

Figure 2:

![CALPHAD isothermal equilibrium at 480 C](./figures/fig2_isothermal_480C.png)

Generated by:
* [`notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb`](./notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb)

### Figures Generated Inline in Notebooks

The following plots are generated inside notebooks but are not currently saved as standalone PNG files:

* Strengthening comparison bar chart in [`2.strength_model.ipynb`](./notebooks/li_et_al_2024/2.strength_model.ipynb)
* DFT clustered vs dispersed Delta E bar chart in [`3.dft_clustering.ipynb`](./notebooks/li_et_al_2024/3.dft_clustering.ipynb)

### Legacy Supporting Figures

These figures are from earlier supporting notebooks and remain useful background:

| Figure | File | Notebook |
| --- | --- | --- |
| Phase fraction vs T | [`figures/maraging_phase_fraction_vs_T.png`](./figures/maraging_phase_fraction_vs_T.png) | [`notebooks/2.equilibrium.ipynb`](./notebooks/2.equilibrium.ipynb) |
| Isothermal comparison | [`figures/fig2_isothermal_comparison.png`](./figures/fig2_isothermal_comparison.png) | [`notebooks/2.equilibrium.ipynb`](./notebooks/2.equilibrium.ipynb) |
| SCF convergence | [`figures/fig3_scf_convergence.png`](./figures/fig3_scf_convergence.png) | [`notebooks/3.dft_visualisation.ipynb`](./notebooks/3.dft_visualisation.ipynb) |
| Formation energy comparison | [`figures/fig4_formation_energy_comparison.png`](./figures/fig4_formation_energy_comparison.png) | [`notebooks/3.dft_visualisation.ipynb`](./notebooks/3.dft_visualisation.ipynb) |
| Ni3Ti energy trace | [`figures/fig5_ni3ti_energy_trace.png`](./figures/fig5_ni3ti_energy_trace.png) | [`notebooks/3.dft_visualisation.ipynb`](./notebooks/3.dft_visualisation.ipynb) |

## What We Replicated

### Strong Replication

* The alloy composition from Li et al. was implemented directly.
* CALPHAD predicts the correct qualitative long-aging phase families: BCC matrix, ETA/Ni3Ti, LAVES/Mo-rich, and SIGMA/Cr-related phase.
* The Ni3Ti strengthening notebook reproduces the paper's main mechanism conclusion: particle shearing dominates over Orowan bypassing for Ni3Ti at the SA30000 size scale.
* The coherency strengthening value for Ni3Ti is close to the paper value.
* All five VPS DFT output files in `output_vm1` converged successfully.

### Partial Replication

* The DFT clustering calculation is a simplified Fe54 Ni/Mo model. It supports the kinetic clustering argument, but it is not the same as the paper's Fe-Co-X model set.
* The strengthening model covers Ni3Ti in detail, but it does not yet fully reproduce Table 4 for every precipitate and aging state.
* CALPHAD gives qualitative agreement in phase identities, but quantitative phase fractions differ from APT volume fractions.

### Not Replicated

* Hardness and engineering stress-strain curves from Fig. 1.
* EBSD, XRD, Williamson-Hall, and dislocation density analysis from Fig. 2.
* TEM/HRTEM/FFT and APT reconstructions from Figs. 3 to 7.
* Full Fig. 8 DFT dataset including Co-containing supercells, Cr cases, and multiple X concentrations.
* Full Fig. 9 yield strength decomposition across ST, SA30, SA300, SA3000, and SA30000.
* Reverted austenite TRIP analysis from Section 4.3.

## Limitations

1. CALPHAD is equilibrium-based, while the paper studies time-dependent aging.
2. CALPHAD outputs mole fractions, while the paper's APT values are volume fractions.
3. The DFT supercells are fixed-cell SCF calculations and are not fully relaxed.
4. The DFT supercells omit Co, Cr, Ti, Si, and C, even though the real alloy contains them.
5. The DFT work currently covers Ni and Mo but not Cr.
6. The strengthening model currently focuses on Ni3Ti, not every precipitate type in Table 4.
7. Some equation formatting in the extracted paper text is corrupted, so the strengthening notebook uses the standard readable forms consistent with the paper constants.

## How to Reproduce

### Python Notebooks

Install dependencies:

```bash
pip install numpy matplotlib pycalphad jupyter
```

Run the notebooks:

```bash
jupyter notebook notebooks/li_et_al_2024/1.calphad_equilibrium.ipynb
jupyter notebook notebooks/li_et_al_2024/2.strength_model.ipynb
jupyter notebook notebooks/li_et_al_2024/3.dft_clustering.ipynb
```

### DFT Runs

From the repository root:

```bash
cd dft/vps
mkdir -p outdir
mpirun -np 4 pw.x -in fe54_pure.scf.in > fe54_pure.scf.out
mpirun -np 4 pw.x -in fe54_3ni_dispersed.scf.in > fe54_3ni_dispersed.scf.out
mpirun -np 4 pw.x -in fe54_3ni_clustered.scf.in > fe54_3ni_clustered.scf.out
mpirun -np 4 pw.x -in fe54_5mo_dispersed.scf.in > fe54_5mo_dispersed.scf.out
mpirun -np 4 pw.x -in fe54_5mo_clustered.scf.in > fe54_5mo_clustered.scf.out
```

Validate outputs:

```bash
grep -E "JOB DONE|convergence NOT achieved|!    total energy|estimated scf accuracy" *.out
```

Use only outputs that show normal completion and converged final energies.

## Repository Structure

```text
2databases/
  mc_fe_v2062_clean.tdb

dft/
  vps/
    fe54_pure.scf.in
    fe54_3ni_clustered.scf.in
    fe54_3ni_dispersed.scf.in
    fe54_5mo_clustered.scf.in
    fe54_5mo_dispersed.scf.in
    output_vm1/
      fe54_pure.scf.out
      fe54_3ni_clustered.scf.out
      fe54_3ni_dispersed.scf.out
      fe54_5mo_clustered.scf.out
      fe54_5mo_dispersed.scf.out

figures/
  fig1_phase_fraction_vs_T.png
  fig2_isothermal_480C.png
  fig2_isothermal_comparison.png
  fig3_scf_convergence.png
  fig4_formation_energy_comparison.png
  fig5_ni3ti_energy_trace.png

literature_validation/
  main_paper.pdf
  main_paper.txt

notebooks/
  li_et_al_2024/
    1.calphad_equilibrium.ipynb
    2.strength_model.ipynb
    3.dft_clustering.ipynb
```

