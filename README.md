# Maraging Steel Thermodynamic Modeling

## Overview
This project focuses on the computational thermodynamic modeling of an ultra-high strength maraging steel alloy. The specific composition under investigation is **Fe–18Ni-8.5Co–5Mo-0.7Ti-0.2Al (wt.%)**, which is the focus of the included research paper: *"Heterogeneous nucleation of Ni3Ti by Mo-enriched particles enhances strength and fracture toughness of maraging steel"* (Xu et al., 2025).

The primary goal of the provided codebase is to evaluate various Thermodynamic Databases (`.tdb` files) using the CALPHAD approach to determine if they contain the necessary elemental interactions (unary, binary, and ternary) to accurately model this specific alloy. 

## Project Structure
- `structel.pdf`: The reference research paper detailing the microstructure, mechanical properties, precipitation behavior (e.g., Ni3Ti and Mo-enriched particles), and composition of the target maraging steel.
- `02_list_elements.py`: A Python script that parses the `COST507-modified.tdb` database using `pycalphad` and `tinydb`. It extracts and lists available unary, binary, ternary, and higher-order interactions for the target elements (`Fe`, `Ni`, `Co`, `Mo`, `Ti`, `Al`), and identifies missing interactions.
- `03.py`: A similar Python script configured to analyze another database (e.g., `mc_fecocrnbti.tdb`). It provides a coverage summary of found vs. needed binary and ternary interactions for our specific system.
- `our_use_case.txt`: Contains the output/summary of a database analysis, showing exactly which elements and specific phase interactions are covered or missing for the target alloy.
- `COST507-modified.tdb`: A modified version of the COST507 thermodynamic database used for the analysis.
- `prop_plot.ipynb` & `1.testPycalphadVersion.ipynb`: Auxiliary Jupyter notebooks for plotting properties and testing `pycalphad` environments. 

## Requirements
To run the database analysis scripts, you need Python and the following libraries:
- `pycalphad`
- `tinydb`

## Usage
Run the analysis scripts to evaluate a specific `.tdb` database against the target maraging steel composition:

```bash
python 02_list_elements.py
python 03.py
```

These scripts will output a detailed breakdown of the available and missing thermodynamic parameters. This is a crucial first step in determining if a database is suitable for simulating the phase equilibria described in the reference paper.