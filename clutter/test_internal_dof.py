import numpy as np
import xarray as xr
from pycalphad import Database, equilibrium, variables as v

DB_PATH = '2databases/mc_fe_v2062_clean.tdb'
db = Database(DB_PATH)

COMPONENTS = ['FE', 'CR', 'CO', 'NI', 'TI', 'MO', 'SI', 'C', 'VA']
PHASES = ['LIQUID', 'BCC_A2', 'BCC_B2', 'FCC_A1', 'HCP_A3', 'ETA', 'LAVES_PHASE', 'SIGMA', 'NITI2', 'M23C6', 'CHI_A12', 'MU_PHASE']

comp = {'CR': 0.12017, 'CO': 0.03855, 'NI': 0.07742, 'TI': 0.00593, 'MO': 0.02960, 'SI': 0.00202, 'C': 0.00009}

iso_result = equilibrium(
    db, COMPONENTS, PHASES,
    {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
     v.X('TI'): comp['TI'], v.X('CR'): comp['CR'], v.X('SI'): comp['SI'],
     v.X('C'): comp['C'],
     v.T: 480 + 273.15, v.P: 101325}
)

for v_idx in range(iso_result.sizes['vertex']):
    ph = str(iso_result.Phase.squeeze().isel(vertex=v_idx).values)
    print(f"Vertex {v_idx} Phase: '{ph}'")
    if 'ETA' in ph:
        y_vals = iso_result.Y.squeeze().isel(vertex=v_idx).values
        print("ETA Y:", y_vals)
    if 'BCC_A2' in ph:
        y_vals = iso_result.Y.squeeze().isel(vertex=v_idx).values
        print("BCC Y:", y_vals)
