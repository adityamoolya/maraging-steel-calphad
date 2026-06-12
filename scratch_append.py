import nbformat as nbf

# Read the notebook
with open('notebooks/1.setup.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

md_cell = nbf.v4.new_markdown_cell("""## Database Sanity Check (Binary Phase Diagrams)

To validate the `mc_fe_v2062_clean.tdb` database parameters, we can plot the binary phase diagrams of Fe-Ni and Fe-Ti. These should match standard literature phase diagrams.
- **Fe-Ni** should show the classic $\\gamma$-austenite (FCC) field and $\\alpha$-ferrite (BCC) field.
- **Fe-Ti** should clearly show the Laves phase ($Fe_2Ti$) intermediate compound.
""")

code_cell = nbf.v4.new_code_cell("""from pycalphad import Database, binplot
import pycalphad.variables as v
import matplotlib.pyplot as plt

# Suppress pycalphad warnings for cleaner output
import warnings
warnings.filterwarnings('ignore')

db = Database('../databases/mc_fe_v2062_clean.tdb')

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# --- Fe-Ni Binary ---
comps_feni = ['FE', 'NI', 'VA']
# Limit phases to main ones for speed and clarity
phases_feni = ['LIQUID', 'FCC_A1', 'BCC_A2', 'BCC_B2']
print("Calculating Fe-Ni binary phase diagram...")
binplot(db, comps_feni, phases_feni, {v.X('NI'): (0, 1, 0.02), v.T: (500, 2000, 20), v.P: 101325}, ax=axes[0])
axes[0].set_title("Fe-Ni Binary Phase Diagram")

# --- Fe-Ti Binary ---
comps_feti = ['FE', 'TI', 'VA']
phases_feti = ['LIQUID', 'FCC_A1', 'BCC_A2', 'HCP_A3', 'LAVES_PHASE']
print("Calculating Fe-Ti binary phase diagram...")
binplot(db, comps_feti, phases_feti, {v.X('TI'): (0, 1, 0.02), v.T: (500, 2000, 20), v.P: 101325}, ax=axes[1])
axes[1].set_title("Fe-Ti Binary Phase Diagram")

plt.tight_layout()
plt.show()
print("Plots generated.")
""")

nb['cells'].extend([md_cell, code_cell])

# Write back
with open('notebooks/1.setup.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Successfully added validation blocks to notebook 1.")
