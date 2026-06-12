import matplotlib.pyplot as plt
import numpy as np
from pycalphad import Database, equilibrium, variables as v

DB_PATH = '../databases/mc_fe_v2062_clean.tdb'
db = Database(DB_PATH)

COMPONENTS = ['FE', 'NI', 'CO', 'MO', 'TI', 'AL', 'VA']
comp = {
    'FE': 69.747,
    'NI': 17.670,
    'CO': 8.310,
    'MO': 3.003,
    'TI': 0.843,
    'AL': 0.427
}

comp_frac = {k: v_val/100.0 for k, v_val in comp.items()}
PHASES = list(db.phases.keys())

result_sweep = equilibrium(
    db, COMPONENTS, PHASES,
    {v.X('NI'): comp_frac['NI'], v.X('CO'): comp_frac['CO'], v.X('MO'): comp_frac['MO'],
     v.X('TI'): comp_frac['TI'], v.X('AL'): comp_frac['AL'],
     v.T: [600, 1000], v.P: 101325}
)

print("Phases present:")
print(result_sweep.Phase.values)
