"""
NEB minimum energy path profile from the converged CI-NEB run.
7 images, converged at iteration 11.

Generates: figures/neb_energy_path.png
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# ── Converged image energies from neb.out iteration 11 ──
image_energies_eV = np.array([
    -51810.2245030,   # Image 1 (start endpoint, frozen)
    -51810.0985170,   # Image 2
    -51809.6679019,   # Image 3
    -51809.5634072,   # Image 4 (climbing image = saddle point)
    -51809.6723982,   # Image 5
    -51810.1061683,   # Image 6
    -51810.2244967,   # Image 7 (end endpoint, frozen)
])

# ── Shift to reference = endpoint average ──
E_ref = (image_energies_eV[0] + image_energies_eV[-1]) / 2.0
E_relative = image_energies_eV - E_ref

# ── Reaction coordinate (normalised 0 to 1) ──
n_images = len(image_energies_eV)
reaction_coord = np.linspace(0, 1, n_images)

# ── Spline interpolation for smooth curve ──
from scipy.interpolate import CubicSpline
cs = CubicSpline(reaction_coord, E_relative)
x_smooth = np.linspace(0, 1, 300)
y_smooth = cs(x_smooth)

# ── Barrier height ──
Ea_forward = E_relative[3] - E_relative[0]   # saddle - start
Ea_reverse = E_relative[3] - E_relative[-1]  # saddle - end

# ── Styling ──
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'Helvetica Neue', 'Arial'],
    'font.size': 12,
    'axes.linewidth': 1.2,
    'figure.facecolor': '#0D1117',
    'axes.facecolor': '#161B22',
    'text.color': '#E6EDF3',
    'axes.labelcolor': '#E6EDF3',
    'xtick.color': '#8B949E',
    'ytick.color': '#8B949E',
    'axes.edgecolor': '#30363D',
    'grid.color': '#21262D',
    'grid.alpha': 0.8,
})

fig, ax = plt.subplots(figsize=(10, 6.5))

# Smooth path
ax.plot(x_smooth, y_smooth, color='#58A6FF', linewidth=2.5, zorder=2, alpha=0.7)

# Image markers
colors = ['#3FB950' if i in (0, 6) else '#F85149' if i == 3 else '#58A6FF'
          for i in range(n_images)]
labels_map = {0: 'Ni @ (¼,¼,¼)', 3: 'Saddle point', 6: 'Ni @ (0,0,0)'}

for i, (x, y) in enumerate(zip(reaction_coord, E_relative)):
    ax.plot(x, y, 'o', color=colors[i], markersize=12, zorder=5,
            markeredgecolor='white', markeredgewidth=1.8)
    if i in labels_map:
        offset = (0, 15) if i != 3 else (0, -22)
        va = 'bottom' if i != 3 else 'top'
        ax.annotate(labels_map[i], xy=(x, y), xytext=offset,
                    textcoords='offset points', fontsize=10,
                    ha='center', va=va, color=colors[i], fontweight='bold')

# Barrier annotation arrow
ax.annotate('', xy=(0.5, E_relative[3]), xytext=(0.5, E_relative[0]),
            arrowprops=dict(arrowstyle='<->', color='#F0883E', lw=2))
ax.text(0.54, (E_relative[3] + E_relative[0]) / 2,
        f'$E_a$ = {Ea_forward:.3f} eV\n({Ea_forward * 96.485:.1f} kJ/mol)',
        fontsize=12, color='#F0883E', fontweight='bold', va='center')

# Frozen endpoint markers
for i in [0, 6]:
    ax.annotate('frozen', xy=(reaction_coord[i], E_relative[i]),
                xytext=(0, -18), textcoords='offset points',
                fontsize=8, ha='center', color='#8B949E', style='italic')

ax.set_xlabel('Reaction Coordinate', fontsize=13)
ax.set_ylabel('Energy relative to endpoints (eV)', fontsize=13)
ax.set_title(
    'CI-NEB Minimum Energy Path: Ni Migration in BCC Fe\n'
    '2×2×2 supercell (15 atoms)  |  7 images  |  converged in 11 iterations',
    fontsize=13, fontweight='bold', color='#E6EDF3',
)
ax.grid(True, alpha=0.3)
ax.set_xlim(-0.05, 1.05)

plt.tight_layout()
plt.savefig('figures/neb_energy_path.png', dpi=200, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print('Saved figures/neb_energy_path.png')
plt.close()
