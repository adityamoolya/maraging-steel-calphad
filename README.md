# DFT-Informed Thermodynamics of Maraging Steel Aging

This project aims to provide a computational thermodynamic explanation for the precipitation behavior observed in recent experimental literature on ultra-high strength maraging steels (e.g., *Heterogeneous nucleation of Ni3Ti by Mo-enriched particles enhances strength and fracture toughness of maraging steel*, Xu et al., 2025).

## Overall Objective
Use Density Functional Theory (DFT) formation energies to support CALPHAD modeling of aging and precipitation in Fe-Ni-Co-Mo-Ti-Al alloys, explaining the transition from Mo-enriched clusters to Ni3Ti ($\eta$) precipitates.

## Project Roadmap

### Phase 1: CALPHAD Thermodynamic Baseline (Completed)
*   **Goal:** Calculate thermodynamic driving forces and equilibrium phase fractions for the maraging steel composition at the experimentally relevant Duplex Aging Treatment (DAT) temperatures (370 °C and 480 °C).
*   **Tool:** Python (`pycalphad`) + `mc_fe_v2062_clean.tdb` database.
*   **Action Items:**
    *   Validate the database's default behavior (Completed).
    *   Suspend competing metastable phases (like $\gamma^\prime$) to force the solver to evaluate the driving force for $\eta$-Ni₃Ti. (Completed)
    *   Extract the driving forces for Mo-rich phases (Fe₇Mo₂, Laves, $\mu$-phase) at 370 °C to prove they form first. (Completed)
    *   Extract driving forces for Ni₃Ti at 480 °C. (Completed)

### Phase 2: DFT Formation Energies (Current Phase)
*   **Goal:** Calculate exact 0 K formation energies for the relevant phases from first principles to verify or correct the CALPHAD database.
*   **Tool:** Quantum ESPRESSO (or similar DFT code).
*   **Action Items:**
    *   Set up unit cells for BCC Fe matrix, $\eta$-Ni₃Ti, and Fe₇Mo₂ (or relevant Mo-cluster structure).
    *   Run structural relaxations and total energy calculations.
    *   Compare the DFT formation energies against the enthalpy values used in the CALPHAD `.tdb` file.

### Phase 3: Phase-Field Modeling (Optional / Stretch Goal)
*   **Goal:** Simulate the spatial and temporal evolution of the precipitates to visually match the microscopy images from the paper.
*   **Tool:** MICRESS, MOOSE, or PRISMA (kinetics).
*   **Action Items:**
    *   Input CALPHAD driving forces and DFT interfacial energies to model heterogeneous nucleation of Ni₃Ti on Mo-particles.
    *   *Note: This is considered a stretch goal because setting up a multi-component kinetic model requires significant parameter tuning and computational time.*