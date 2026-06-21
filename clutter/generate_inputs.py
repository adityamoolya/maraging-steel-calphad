import os

# Base parameters
ecutwfc = 45
ecutrho = 360
kpoints_supercell = "2 2 2 0 0 0"

# Generate 54-atom BCC lattice positions
a0 = 5.416 # Bohr
super_a = 3 * a0
atoms = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            # Corner atom
            atoms.append([float(i)/3, float(j)/3, float(k)/3])
            # Center atom
            atoms.append([(i+0.5)/3, (j+0.5)/3, (k+0.5)/3])

def write_qe_input(filename, elements, positions, prefix, kpoints="2 2 2 0 0 0"):
    n_atoms = len(positions)
    n_types = len(set(elements))
    
    # Calculate starting magnetization: roughly 2.0-2.5 for Fe, 0.6 for Ni, 0 for Mo
    mag = []
    types_present = list(set(elements))
    for t in types_present:
        if t == 'Fe':
            mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.5")
        elif t == 'Ni':
            mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.2")
        elif t == 'Mo':
            mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.0")

    mag_str = "\n  ".join(mag)
    
    species_str = ""
    for idx, t in enumerate(types_present):
        if t == 'Fe':
            species_str += "  Fe  55.845  Fe.pbe-spn-rrkjus_psl.1.0.0.UPF\n"
        elif t == 'Ni':
            species_str += "  Ni  58.693  Ni.pbe-nd-rrkjus.UPF\n"
        elif t == 'Mo':
            species_str += "  Mo  95.95   Mo.pbe-spn-rrkjus_psl.1.0.0.UPF\n"

    pos_str = ""
    for idx, (el, pos) in enumerate(zip(elements, positions)):
        pos_str += f"  {el} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n"

    template = f"""&CONTROL
  calculation = 'vc-relax'
  prefix = '{prefix}'
  outdir = './outdir'
  pseudo_dir = './'
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
  ecutwfc = {ecutwfc}
  ecutrho = {ecutrho}
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
&CELL
  cell_dynamics = 'bfgs'
/
ATOMIC_SPECIES
{species_str}
ATOMIC_POSITIONS (crystal)
{pos_str}
K_POINTS (automatic)
  {kpoints}
"""
    with open(f"dft/{filename}", 'w') as f:
        f.write(template)

# 1. Pure Mo BCC reference
write_qe_input(
    filename="mo_bcc.scf.in",
    elements=["Mo"],
    positions=[[0,0,0]],
    prefix="mo_bcc",
    kpoints="8 8 8 0 0 0"
)
# Modify it to be scf
with open("dft/mo_bcc.scf.in", "r") as f:
    text = f.read().replace("'vc-relax'", "'scf'").replace("celldm(1) = 16.2480", "celldm(1) = 5.95").replace("&IONS\n  ion_dynamics = 'bfgs'\n/\n&CELL\n  cell_dynamics = 'bfgs'\n/\n", "")
with open("dft/mo_bcc.scf.in", "w") as f:
    f.write(text)

# 2. 3-Ni Dispersed
# Fe54, replace 3 atoms far apart.
# Indices to replace: 0 (0,0,0), 26 (0.33, 0.66, 0.33), 52 (0.66, 0.33, 0.66)
elements = ['Fe'] * 54
elements[0] = 'Ni'
elements[18] = 'Ni' # corresponds to (1/3, 0, 0)
elements[45] = 'Ni' # corresponds to (2/3, 1/3, 1/3)
# To make them more dispersed:
elements[0] = 'Ni'
elements[20] = 'Ni' # middle of cell
elements[53] = 'Ni' # opposite corner

# Wait, let's manually pick well-separated indices.
pos_list = atoms
dists = []
def dist(p1, p2):
    # pbc distance in crystal coords
    dx = abs(p1[0]-p2[0]); dx = min(dx, 1-dx)
    dy = abs(p1[1]-p2[1]); dy = min(dy, 1-dy)
    dz = abs(p1[2]-p2[2]); dz = min(dz, 1-dz)
    return dx**2 + dy**2 + dz**2

# Just pick index 0, 27, 53
elements_disp_ni = ['Fe'] * 54
elements_disp_ni[0] = 'Ni'
elements_disp_ni[26] = 'Ni'
elements_disp_ni[53] = 'Ni'
write_qe_input("fe54_3ni_dispersed.in", elements_disp_ni, atoms, "fe54_3ni_disp")

# 3. 3-Ni Clustered
# Nearest neighbors in BCC: (0,0,0) and (0.166, 0.166, 0.166) in crystal coords for 3x3x3 cell
# Specifically atoms[0] = (0,0,0), atoms[1] = (0.5/3, 0.5/3, 0.5/3) = (0.166, 0.166, 0.166)
# atoms[2] = (0,0,1/3) -> not NN. The other NN to 0 is (-0.5/3, -0.5/3, -0.5/3) or (-0.5/3, 0.5/3, 0.5/3).
# Let's pick 0, 1, and 3 where 3 is (0, 1/3, 0). Distance between 1 and 3: dx=0.166, dy=0.166, dz=0.166 -> NN!
elements_clust_ni = ['Fe'] * 54
elements_clust_ni[0] = 'Ni'
elements_clust_ni[1] = 'Ni' # NN to 0
# Find another NN to 0 or 1
nn_idx = 1
for i in range(2, 54):
    if abs(dist(atoms[0], atoms[i]) - 0.75*(1/9)) < 1e-5:
        nn_idx = i
        break
elements_clust_ni[nn_idx] = 'Ni'
write_qe_input("fe54_3ni_clustered.in", elements_clust_ni, atoms, "fe54_3ni_clust")

# 4. 5-Mo Dispersed
elements_disp_mo = ['Fe'] * 54
# Pick 5 atoms spread out
disp_idxs = [0, 13, 26, 39, 52]
for i in disp_idxs:
    elements_disp_mo[i] = 'Mo'
write_qe_input("fe54_5mo_dispersed.in", elements_disp_mo, atoms, "fe54_5mo_disp")

# 5. 5-Mo Clustered
elements_clust_mo = ['Fe'] * 54
# Center atom: 0
elements_clust_mo[0] = 'Mo'
# 4 NN atoms to 0
count = 0
for i in range(1, 54):
    if abs(dist(atoms[0], atoms[i]) - 0.75*(1/9)) < 1e-5:
        elements_clust_mo[i] = 'Mo'
        count += 1
        if count == 4:
            break
write_qe_input("fe54_5mo_clustered.in", elements_clust_mo, atoms, "fe54_5mo_clust")
