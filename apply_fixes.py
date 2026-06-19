import os

files = ['fe54_3ni_dispersed.in', 'fe54_3ni_clustered.in', 'fe54_5mo_dispersed.in', 'fe54_5mo_clustered.in']
for f in files:
    path = os.path.join('dft', f)
    with open(path, 'r') as file:
        lines = file.readlines()
    
    new_lines = []
    skip_cell = False
    for line in lines:
        if "calculation = 'vc-relax'" in line:
            new_lines.append("  calculation = 'relax'\n")
        elif "Ni  58.693  Ni.pbe-nd-rrkjus.UPF" in line:
            new_lines.append("  Ni  58.693  Ni.pbe-spn-rrkjus_psl.1.0.0.UPF\n")
        elif "&CELL" in line:
            skip_cell = True
        elif skip_cell and "/" in line:
            skip_cell = False
        elif skip_cell:
            continue
        elif "2 2 2 0 0 0" in line:
            new_lines.append("  3 3 3 0 0 0\n")
        else:
            new_lines.append(line)
            
    with open(path, 'w') as file:
        file.writelines(new_lines)

print("Files updated.")
