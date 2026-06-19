import os
a0 = 5.416
super_a = 3 * a0
atoms = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            atoms.append([float(i)/3, float(j)/3, float(k)/3])
            atoms.append([(i+0.5)/3, (j+0.5)/3, (k+0.5)/3])

def write_qe_input(filename, elements, positions, prefix, kpoints="2 2 2 0 0 0"):
    n_atoms = len(positions)
    n_types = len(set(elements))
    types_present = list(set(elements))
    mag = []
    for t in types_present:
        if t == "Fe": mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.5")
        elif t == "Ni": mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.2")
        elif t == "Mo": mag.append(f"starting_magnetization({types_present.index(t)+1}) = 0.0")
    mag_str = "\n  ".join(mag)
    
    species_str = ""
    for idx, t in enumerate(types_present):
        if t == "Fe": species_str += "  Fe  55.845  Fe.pbe-spn-rrkjus_psl.1.0.0.UPF\n"
        elif t == "Ni": species_str += "  Ni  58.693  Ni.pbe-nd-rrkjus.UPF\n"
        elif t == "Mo": species_str += "  Mo  95.95   Mo.pbe-spn-rrkjus_psl.1.0.0.UPF\n"

    pos_str = ""
    for idx, (el, pos) in enumerate(zip(elements, positions)):
        pos_str += f"  {el} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n"

    template = f"""&CONTROL
  calculation = 'vc-relax'
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
&CELL
  cell_dynamics = 'bfgs'
/
ATOMIC_SPECIES
{species_str}ATOMIC_POSITIONS (crystal)
{pos_str}K_POINTS (automatic)
  {kpoints}
"""
    with open("dft/"+filename, "w") as f:
        f.write(template)

elements_disp_ni = ["Fe"] * 54
for i in [2, 30, 46]: elements_disp_ni[i] = "Ni"
write_qe_input("fe54_3ni_dispersed.in", elements_disp_ni, atoms, "fe54_3ni_disp")

elements_disp_mo = ["Fe"] * 54
for i in [48, 11, 33, 37, 4]: elements_disp_mo[i] = "Mo"
write_qe_input("fe54_5mo_dispersed.in", elements_disp_mo, atoms, "fe54_5mo_disp")
