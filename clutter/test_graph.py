import numpy as np
from pycalphad import Database, equilibrium, variables as v

DB_PATH = 'databases/mc_fe_v2062_clean.tdb'
db = Database(DB_PATH)

COMPONENTS = ['FE', 'NI', 'CO', 'MO', 'TI', 'AL', 'VA']
# Weight fractions
wt_frac = {'NI': 0.180, 'CO': 0.085, 'MO': 0.050, 'TI': 0.007, 'AL': 0.002}
wt_frac['FE'] = 1.0 - sum(wt_frac.values())

AW = {'FE': 55.845, 'NI': 58.693, 'CO': 58.933, 'MO': 95.94, 'TI': 47.867, 'AL': 26.982}
moles = {el: wt_frac[el] / AW[el] for el in AW}
total_moles = sum(moles.values())
comp = {el: moles[el] / total_moles for el in moles}

PHASES = list(db.phases.keys())

res = equilibrium(
    db, COMPONENTS, PHASES,
    {v.X('NI'): comp['NI'], v.X('CO'): comp['CO'], v.X('MO'): comp['MO'],
     v.X('TI'): comp['TI'], v.X('AL'): comp['AL'],
     v.T: [600, 800, 1000], v.P: 101325}
)

for t_idx, T in enumerate([600, 800, 1000]):
    print(f"--- T = {T} K ---")
    phases = res.Phase.isel(T=t_idx, P=0).values.flatten()
    np_vals = res.NP.isel(T=t_idx, P=0).values.flatten()
    for ph, frac in zip(phases, np_vals):
        if ph != '' and frac > 0.001:
            print(f"{ph}: {frac:.4f}")
