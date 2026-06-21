import numpy as np

atoms = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            atoms.append([float(i)/3, float(j)/3, float(k)/3])
            atoms.append([(i+0.5)/3, (j+0.5)/3, (k+0.5)/3])

def dist_pbc(p1, p2):
    d = []
    for x, y in zip(p1, p2):
        delta = abs(x - y)
        delta = min(delta, 1.0 - delta)
        d.append(delta)
    return np.sqrt(d[0]**2 + d[1]**2 + d[2]**2)

# Maximize min distance for 3 atoms
best_3 = []
max_min_d3 = 0
for i in range(54):
    for j in range(i+1, 54):
        d1 = dist_pbc(atoms[i], atoms[j])
        if d1 < 0.4: continue
        for k in range(j+1, 54):
            d2 = dist_pbc(atoms[i], atoms[k])
            d3 = dist_pbc(atoms[j], atoms[k])
            min_d = min(d1, d2, d3)
            if min_d > max_min_d3:
                max_min_d3 = min_d
                best_3 = [i, j, k]

# Maximize min distance for 5 atoms
best_5 = []
max_min_d5 = 0
import random
random.seed(42)
# Too many combinations (54 C 5 = 3.1 million), just do random search
for _ in range(50000):
    idx = random.sample(range(54), 5)
    min_d = 1.0
    for a in range(5):
        for b in range(a+1, 5):
            d = dist_pbc(atoms[idx[a]], atoms[idx[b]])
            if d < min_d: min_d = d
    if min_d > max_min_d5:
        max_min_d5 = min_d
        best_5 = idx

print("Best 3 Ni:", best_3, "Min dist:", max_min_d5)
print("Distances 3 Ni:")
for a in range(3):
    for b in range(a+1, 3):
        print(dist_pbc(atoms[best_3[a]], atoms[best_3[b]]))

print("Best 5 Mo:", best_5, "Min dist:", max_min_d5)
print("Distances 5 Mo:")
for a in range(5):
    for b in range(a+1, 5):
        print(dist_pbc(atoms[best_5[a]], atoms[best_5[b]]))
