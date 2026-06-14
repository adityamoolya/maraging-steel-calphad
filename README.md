# DFT-Informed Thermodynamics of Maraging Steel Aging

This project aims to provide a computational thermodynamic explanation for the precipitation behavior observed in recent experimental literature on ultra-high strength maraging steels.

## Overall Objective
Use Density Functional Theory (DFT) formation energies to support CALPHAD modeling of precipitation in Fe-Ni-Co-Mo-Ti-Al alloys, and potentially utilize these results as a foundation for Phase-Field kinetic modeling of aging.

## Literature Validation
The experimental baseline for this project is drawn from literature studying the heterogeneous nucleation of Ni₃Ti ($\eta$) and Mo-enriched clusters. 
*   **Key Reference:** *Heterogeneous nucleation of Ni₃Ti by Mo-enriched particles enhances strength and fracture toughness of maraging steel* (Xu et al., 2025).
*   **Reference Papers:** The original PDFs validating the discrepancy between CALPHAD phase fraction predictions and true experimental observations (such as 12% $\eta$-Ni₃Ti phase fraction) have been archived in the `literature_validation/` directory.

## Project Roadmap

### Phase 1: CALPHAD Thermodynamic Baseline (Completed)
*   **Goal:** Calculate thermodynamic driving forces and equilibrium phase fractions for the maraging steel composition at the experimentally relevant Duplex Aging Treatment (DAT) temperatures (370 °C and 480 °C).
*   **Tool:** Python (`pycalphad`) + `mc_fe_v2062_clean.tdb` database.
*   **Results:** 
    *   Validated the database's default behavior and isolated competing metastable phases.
    *   Successfully extracted driving forces, finding that CALPHAD databases under-predicted the experimental stability and phase fraction of $\eta$-Ni₃Ti.

### Phase 2: DFT Formation Energies (Completed)
*   **Goal:** Calculate exact 0 K formation energies for the relevant phases from first principles to verify the fundamental quantum stability of $\eta$-Ni₃Ti.
*   **Tool:** Quantum ESPRESSO.
*   **Results:**
    *   **Pure Ni (FCC):** $-339.4432$ Ry / atom
    *   **Pure Ti (HCP):** $-119.7367$ Ry / atom
    *   **$\eta$-Ni₃Ti (16-atom D0₂₄ cell):** $-4552.7879$ Ry 
    *   **Formation Energy ($\Delta H_f$):** **$-0.444 \text{ eV/atom}$** ($-42.8 \text{ kJ/mol}$)
*   **Conclusion:** The strongly negative $\Delta H_f$ provides strict fundamental proof that $\eta$-Ni₃Ti is a deep thermodynamic well. This validates the experimental observations (Xu et al., 2025) and computationally proves that default CALPHAD parameters under-predict its stability.
*   **Troubleshooting Log:**
    *   *Pseudopotential Mismatch Bug:* Initial computations yielded unphysical values because Ni used the older `nd-rrkjus` library, while Ti used the newer `psl.1.0.0` library with explicit semi-core electrons. Fixed by enforcing strictly matching `psl.1.0.0` libraries.
    *   *Symmetry Coordinate Bug:* A manual coordinate typo in the 6h Wyckoff positions caused atomic overlaps, resulting in a $+38$ Ry energy penalty. Fixed by rigorously mapping to $P6_3/mmc$ crystallographic symmetry (resulting in the final `_v3` input).

### Phase 3: Phase-Field Modeling (Future Work / Extension)
*   **Goal:** Simulate the spatial and temporal evolution (kinetics) of the precipitates during the aging process to visually map the growth of Ni₃Ti.
*   **Tool:** Python (`FiPy`) or similar Phase-Field solvers.
*   **Context:** While CALPHAD solves for infinite-time thermodynamic equilibrium, Phase-Field solving Cahn-Hilliard and Allen-Cahn PDE equations is required to model the explicit *time-dependent* kinetics of aging. This serves as a potential extension if dynamic microstructural evolution modeling is requested.