"""
NEB convergence plot: activation energy vs iteration.
Shows the barrier dropping from ~0.86 eV to 0.661 eV over 11 iterations.

Generates: figures/neb_convergence.png
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Activation energies from neb.out (forward direction) ──
iterations = np.arange(1, 12)
Ea_per_iter = np.array([
    0.859905,  # iter 1
    0.830902,  # iter 2
    0.782119,  # iter 3
    0.728653,  # iter 4
    0.686242,  # iter 5
    0.664569,  # iter 6
    0.662193,  # iter 7
    0.662007,  # iter 8
    0.661768,  # iter 9
    0.661421,  # iter 10
    0.661096,  # iter 11
])

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

fig, ax = plt.subplots(figsize=(9, 6))

# Main curve
ax.plot(iterations, Ea_per_iter, 'o-', color='#58A6FF', linewidth=2.5,
        markersize=9, markeredgecolor='white', markeredgewidth=1.5, zorder=4)

# Converged value line
ax.axhline(Ea_per_iter[-1], color='#3FB950', linestyle='--', linewidth=1.5,
           alpha=0.7, zorder=2)
ax.text(11.3, Ea_per_iter[-1], f'{Ea_per_iter[-1]:.3f} eV\n(converged)',
        fontsize=10, color='#3FB950', va='center', fontweight='bold')

# Old 1-iteration estimate
ax.axhline(0.920, color='#F85149', linestyle=':', linewidth=1.5, alpha=0.5, zorder=2)
ax.text(1.3, 0.925, 'Old estimate (1 iter, 3 images): 0.92 eV',
        fontsize=9, color='#F85149', alpha=0.8)

# Convergence threshold annotation
ax.fill_between([0.5, 11.5], Ea_per_iter[-1] - 0.005, Ea_per_iter[-1] + 0.005,
                color='#3FB950', alpha=0.1, zorder=1)

ax.set_xlabel('NEB Path Iteration', fontsize=13)
ax.set_ylabel('Activation Energy $E_a^{mig}$ (eV)', fontsize=13)
ax.set_title(
    'CI-NEB Convergence: Ni Migration Barrier in BCC Fe\n'
    'Barrier drops from 0.86 → 0.661 eV with proper path optimization',
    fontsize=13, fontweight='bold', color='#E6EDF3',
)
ax.grid(True, alpha=0.3)
ax.set_xlim(0.5, 12)
ax.set_ylim(0.6, 0.95)
ax.set_xticks(iterations)

plt.tight_layout()
plt.savefig('figures/neb_convergence.png', dpi=200, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print('Saved figures/neb_convergence.png')
plt.close()
