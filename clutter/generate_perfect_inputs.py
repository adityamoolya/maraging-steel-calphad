import os
import numpy as np

a0 = 5.416
super_a = 3 * a0

# Generate 54-atom BCC lattice positions
atoms = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            atoms.append([float(i)/3, float(j)/3, float(k)/3])
            atoms.append([(i+0.5)/3, (j+0.5)/3, (k+0.5)/3])

def write_qe_input(filename, elements, positions, prefix):
    n_atoms = len(positions)
    types_present = list(set(elements))
    n_types = len(types_present)
    
    mag = []
    for t in types_present:
        if t == "Fe": mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.5")
        elif t == "Ni": mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.2")
        elif t == "Mo": mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.0")
    mag_str = "\n  ".join(mag)
    
    species_str = ""
    for t in types_present:
        if t == "Fe": species_str += "  Fe  55.845  Fe.pbe-spn-rrkjus_psl.1.0.0.UPF\n"
        elif t == "Ni": species_str += "  Ni  58.693  Ni.pbe-spn-rrkjus_psl.1.0.0.UPF\n"
        elif t == "Mo": species_str += "  Mo  95.95   Mo.pbe-spn-rrkjus_psl.1.0.0.UPF\n"

    pos_str = ""
    for el, pos in zip(elements, positions):
        pos_str += f"  {el} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n"

    template = f"""&CONTROL
  calculation = 'relax'
  prefix = '{prefix}'
  outdir = './outdir'
  pseudo_dir = './pseudo/'
  tstress = .true.
  tprnfor = .true.
  etot_conv_thr = 1.0d-4
  forc_conv_thr = 1.0d-3
/
&SYSTEM
  ibrav = 1
  celldm(1) = {super_a:.4f}
  nat = {n_atoms}
  ntyp = {n_types}
  ecutwfc = 45
  ecutrho = 360
  occupations = 'smearing'
  smearing = 'm-v'
  degauss = 0.02
  nspin = 2
  {mag_str}
/
&ELECTRONS
  electron_maxstep = 200
  conv_thr = 1.0d-6
  mixing_beta = 0.3
  mixing_mode = 'local-TF'
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
{species_str}ATOMIC_POSITIONS (crystal)
{pos_str}K_POINTS (automatic)
  3 3 3 0 0 0
"""
    with open(os.path.join("dft", filename), "w") as f:
        f.write(template)

# 1. 3-Ni Dispersed
elements = ["Fe"] * 54
for i in [2, 30, 46]: elements[i] = "Ni"
write_qe_input("fe54_3ni_dispersed.in", elements, atoms, "fe54_3ni_disp")

# 2. 3-Ni Clustered
elements = ["Fe"] * 54
elements[0] = "Ni"
elements[1] = "Ni"
# Distances from (0,0,0) -> 0.75*(1/9) in fractional squared is nearest neighbor
for i in range(2, 54):
    dx = min(abs(atoms[0][0]-atoms[i][0]), 1-abs(atoms[0][0]-atoms[i][0]))
    dy = min(abs(atoms[0][1]-atoms[i][1]), 1-abs(atoms[0][1]-atoms[i][1]))
    dz = min(abs(atoms[0][2]-atoms[i][2]), 1-abs(atoms[0][2]-atoms[i][2]))
    if abs((dx**2 + dy**2 + dz**2) - 1/12) < 1e-5:
        elements[i] = "Ni"
        break
write_qe_input("fe54_3ni_clustered.in", elements, atoms, "fe54_3ni_clust")

# 3. 5-Mo Dispersed
elements = ["Fe"] * 54
for i in [48, 11, 33, 37, 4]: elements[i] = "Mo"
write_qe_input("fe54_5mo_dispersed.in", elements, atoms, "fe54_5mo_disp")

# 4. 5-Mo Clustered
elements = ["Fe"] * 54
elements[0] = "Mo"
count = 0
for i in range(1, 54):
    dx = min(abs(atoms[0][0]-atoms[i][0]), 1-abs(atoms[0][0]-atoms[i][0]))
    dy = min(abs(atoms[0][1]-atoms[i][1]), 1-abs(atoms[0][1]-atoms[i][1]))
    dz = min(abs(atoms[0][2]-atoms[i][2]), 1-abs(atoms[0][2]-atoms[i][2]))
    if abs((dx**2 + dy**2 + dz**2) - 1/12) < 1e-5:
        elements[i] = "Mo"
        count += 1
        if count == 4: break
write_qe_input("fe54_5mo_clustered.in", elements, atoms, "fe54_5mo_clust")
