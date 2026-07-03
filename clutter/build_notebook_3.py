import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()

cells = []

cells.append(new_markdown_cell("""# 3. DFT Kinetics: Vacancy Migration Barrier & Diffusion
This notebook reproduces the kinetic analysis of the precipitation sequence using Nudged Elastic Band (NEB) results to calculate the activation energy for Ni solute migration in BCC Fe.
"""))

cells.append(new_markdown_cell("""## 1. NEB Minimum Energy Path
First, let's visualize the converged Climbing-Image NEB (CI-NEB) path (7 images, converged at iteration 11) for the Ni hop into a neighboring vacancy.
"""))

cells.append(new_code_cell("""import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Converged image energies from neb.out iteration 11
image_energies_eV = np.array([
    -51810.2245030,   # Image 1 (start endpoint, frozen)
    -51810.0985170,   # Image 2
    -51809.6679019,   # Image 3
    -51809.5634072,   # Image 4 (climbing image = saddle point)
    -51809.6723982,   # Image 5
    -51810.1061683,   # Image 6
    -51810.2244967,   # Image 7 (end endpoint, frozen)
])

# Shift to reference = endpoint average
E_ref = (image_energies_eV[0] + image_energies_eV[-1]) / 2.0
E_relative = image_energies_eV - E_ref

# Reaction coordinate
n_images = len(image_energies_eV)
reaction_coord = np.linspace(0, 1, n_images)

# Spline interpolation
cs = CubicSpline(reaction_coord, E_relative)
x_smooth = np.linspace(0, 1, 300)
y_smooth = cs(x_smooth)

# Barrier height
Ea_forward = E_relative[3] - E_relative[0]

# Styling
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 12, 'axes.linewidth': 1.2,
    'figure.facecolor': '#0D1117', 'axes.facecolor': '#161B22',
    'text.color': '#E6EDF3', 'axes.labelcolor': '#E6EDF3',
    'xtick.color': '#8B949E', 'ytick.color': '#8B949E',
    'axes.edgecolor': '#30363D', 'grid.color': '#21262D', 'grid.alpha': 0.8,
})

fig, ax = plt.subplots(figsize=(10, 6.5))
ax.plot(x_smooth, y_smooth, color='#58A6FF', linewidth=2.5, zorder=2, alpha=0.7)

colors = ['#3FB950' if i in (0, 6) else '#F85149' if i == 3 else '#58A6FF' for i in range(n_images)]
labels_map = {0: 'Ni @ (¼,¼,¼)', 3: 'Saddle point', 6: 'Ni @ (0,0,0)'}

for i, (x, y) in enumerate(zip(reaction_coord, E_relative)):
    ax.plot(x, y, 'o', color=colors[i], markersize=12, zorder=5, markeredgecolor='white', markeredgewidth=1.8)
    if i in labels_map:
        offset = (0, 15) if i != 3 else (0, -22)
        va = 'bottom' if i != 3 else 'top'
        ax.annotate(labels_map[i], xy=(x, y), xytext=offset, textcoords='offset points', fontsize=10, ha='center', va=va, color=colors[i], fontweight='bold')

ax.annotate('', xy=(0.5, E_relative[3]), xytext=(0.5, E_relative[0]), arrowprops=dict(arrowstyle='<->', color='#F0883E', lw=2))
ax.text(0.54, (E_relative[3] + E_relative[0]) / 2, f'$E_a$ = {Ea_forward:.3f} eV\\n({Ea_forward * 96.485:.1f} kJ/mol)', fontsize=12, color='#F0883E', fontweight='bold', va='center')

ax.set_xlabel('Reaction Coordinate')
ax.set_ylabel('Energy relative to endpoints (eV)')
ax.set_title('CI-NEB Minimum Energy Path: Ni Migration in BCC Fe', fontsize=13, fontweight='bold', color='#E6EDF3')
ax.grid(True, alpha=0.3)
plt.show()
"""))

cells.append(new_markdown_cell("""## 2. NEB Convergence Tracking
We track the convergence of the barrier over the 11 iterations.
"""))

cells.append(new_code_cell("""iterations = np.arange(1, 12)
Ea_per_iter = np.array([
    0.859905, 0.830902, 0.782119, 0.728653, 0.686242, 0.664569, 
    0.662193, 0.662007, 0.661768, 0.661421, 0.661096
])

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(iterations, Ea_per_iter, 'o-', color='#58A6FF', linewidth=2.5, markersize=9, markeredgecolor='white', markeredgewidth=1.5, zorder=4)
ax.axhline(Ea_per_iter[-1], color='#3FB950', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
ax.text(11.3, Ea_per_iter[-1], f'{Ea_per_iter[-1]:.3f} eV\\n(converged)', fontsize=10, color='#3FB950', va='center', fontweight='bold')
ax.axhline(0.920, color='#F85149', linestyle=':', linewidth=1.5, alpha=0.5, zorder=2)
ax.text(1.3, 0.925, 'Old estimate (1 iter, 3 images): 0.92 eV', fontsize=9, color='#F85149', alpha=0.8)

ax.set_xlabel('NEB Path Iteration')
ax.set_ylabel('Activation Energy $E_a^{mig}$ (eV)')
ax.set_title('CI-NEB Convergence: Ni Migration Barrier in BCC Fe', fontsize=13, fontweight='bold', color='#E6EDF3')
ax.grid(True, alpha=0.3)
ax.set_xlim(0.5, 12)
ax.set_xticks(iterations)
plt.show()
"""))

cells.append(new_markdown_cell("""## 3. Total Activation Energy Decomposition
The total activation energy for Ni diffusion in BCC Fe includes the vacancy formation energy and the migration barrier.
"""))

cells.append(new_code_cell("""Ef_vacancy = 2.10
Ea_migration = 0.661
Ea_total = Ef_vacancy + Ea_migration
Ea_expt = 2.49
kJ_per_eV = 96.485

fig, ax = plt.subplots(figsize=(8, 7))
bar_x = [0, 1.2]
bar_width = 0.6

ax.bar(bar_x[0], Ef_vacancy, bar_width, color='#58A6FF', edgecolor='white', linewidth=1.2, label=f'$E_f^v$ (vacancy) = {Ef_vacancy:.2f} eV')
ax.bar(bar_x[0], Ea_migration, bar_width, bottom=Ef_vacancy, color='#F0883E', edgecolor='white', linewidth=1.2, label=f'$E_a^{{mig}}$ (CI-NEB) = {Ea_migration:.3f} eV')
ax.bar(bar_x[1], Ea_expt, bar_width, color='#3FB950', edgecolor='white', linewidth=1.2, alpha=0.8, label=f'Experimental ≈ {Ea_expt:.2f} eV')

ax.text(bar_x[0], Ef_vacancy / 2, f'{Ef_vacancy:.2f} eV', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
ax.text(bar_x[0], Ef_vacancy + Ea_migration / 2, f'{Ea_migration:.3f} eV', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
ax.text(bar_x[0], Ea_total + 0.06, f'Total: {Ea_total:.2f} eV', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#E6EDF3')
ax.text(bar_x[1], Ea_expt / 2, f'{Ea_expt:.2f} eV', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

ax.set_xticks(bar_x)
ax.set_xticklabels(['This Work\\n(DFT-PBE)', 'Experimental\\n(~240 kJ/mol)'], fontsize=12, fontweight='bold')
ax.set_ylabel('Activation Energy (eV)')
ax.set_title('Ni Diffusion Activation Energy in BCC Fe', fontsize=14, fontweight='bold', color='#E6EDF3')
ax.legend(loc='upper right')
ax.set_ylim(0, 3.3)
plt.show()
"""))

cells.append(new_markdown_cell("""## 4. Arrhenius Extrapolation
We extrapolate the hop rate over temperature using the converged activation energy to understand why 480°C was chosen for aging.
"""))

cells.append(new_code_cell("""Ea = 0.661
kB = 8.617e-5
T_ref = 200 + 273.15
T_C = np.linspace(200, 850, 500)
T_K = T_C + 273.15

rate = np.exp(-Ea / (kB * T_K))
rate_ref = np.exp(-Ea / (kB * T_ref))
relative_rate = rate / rate_ref

highlights = {'450°C': (450 + 273.15, '#E07020'), '480°C (Li et al.)': (480 + 273.15, '#9B2D8B')}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(f'Arrhenius Extrapolation of Ni Hop Rate in BCC Fe\\n$E_a$ = {Ea} eV', fontsize=15, fontweight='bold', color='#E6EDF3', y=0.98)

# Panel 1
ax1.semilogy(T_C, relative_rate, color='#58A6FF', linewidth=2.5)
ax1.set_xlabel('Temperature (°C)')
ax1.set_ylabel('Relative Hop Rate (normalised to 200°C)')
ax1.grid(True, alpha=0.3)

for label, (T_hi, color) in highlights.items():
    rate_hi = np.exp(-Ea / (kB * T_hi)) / rate_ref
    T_hi_C = T_hi - 273.15
    ax1.axvline(T_hi_C, color=color, linestyle='--', alpha=0.7)
    ax1.plot(T_hi_C, rate_hi, 'o', color=color, markersize=10, markeredgecolor='white')
    ax1.annotate(f'{label.split(" ")[0]}\\n{rate_hi:.1e}×', xy=(T_hi_C, rate_hi), xytext=(15, -20), textcoords='offset points', fontsize=9.5, color=color, fontweight='bold')

# Panel 2
inv_T = 1000.0 / T_K
ln_rate = -Ea / (kB * T_K)
ax2.plot(inv_T, ln_rate, color='#58A6FF', linewidth=2.5)
ax2.set_xlabel('1000/T  (K⁻¹)')
ax2.set_ylabel('ln(rate) ∝ −$E_a$/$k_B T$')
ax2.grid(True, alpha=0.3)

for label, (T_hi, color) in highlights.items():
    inv_T_hi = 1000.0 / T_hi
    ln_rate_hi = -Ea / (kB * T_hi)
    ax2.plot(inv_T_hi, ln_rate_hi, 'o', color=color, markersize=10, markeredgecolor='white')
    ax2.annotate(label.split(' ')[0], xy=(inv_T_hi, ln_rate_hi), xytext=(15, 10), textcoords='offset points', fontsize=10, color=color, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.show()
"""))

nb.cells = cells
with open('notebooks/li_et_al_2024/3.neb_migration_barrier.ipynb', 'w') as f:
    nbf.write(nb, f)
