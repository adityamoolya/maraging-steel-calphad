"""
Energy decomposition bar chart:
Ef_vacancy + Ea_migration = Ea_diffusion (total)
Compared against experimental target.

Generates: figures/energy_decomposition.png
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Data ──
Ef_vacancy = 2.10       # eV
Ea_migration = 0.661    # eV (converged CI-NEB)
Ea_total = Ef_vacancy + Ea_migration   # 2.761 eV
Ea_expt = 2.49          # eV (~240 kJ/mol)

kJ_per_eV = 96.485

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

fig, ax = plt.subplots(figsize=(8, 7))

bar_x = [0, 1.2]
bar_width = 0.6

# ── This work: stacked bar ──
b1 = ax.bar(bar_x[0], Ef_vacancy, bar_width, color='#58A6FF', edgecolor='white',
            linewidth=1.2, label=f'$E_f^v$ (vacancy) = {Ef_vacancy:.2f} eV', zorder=3)
b2 = ax.bar(bar_x[0], Ea_migration, bar_width, bottom=Ef_vacancy,
            color='#F0883E', edgecolor='white', linewidth=1.2,
            label=f'$E_a^{{mig}}$ (CI-NEB) = {Ea_migration:.3f} eV', zorder=3)

# ── Experimental bar ──
b3 = ax.bar(bar_x[1], Ea_expt, bar_width, color='#3FB950', edgecolor='white',
            linewidth=1.2, alpha=0.8,
            label=f'Experimental ≈ {Ea_expt:.2f} eV ({Ea_expt * kJ_per_eV:.0f} kJ/mol)',
            zorder=3)

# ── Value labels ──
ax.text(bar_x[0], Ef_vacancy / 2, f'{Ef_vacancy:.2f} eV\n({Ef_vacancy * kJ_per_eV:.0f} kJ/mol)',
        ha='center', va='center', fontsize=11, fontweight='bold', color='white')
ax.text(bar_x[0], Ef_vacancy + Ea_migration / 2,
        f'{Ea_migration:.3f} eV\n({Ea_migration * kJ_per_eV:.0f} kJ/mol)',
        ha='center', va='center', fontsize=11, fontweight='bold', color='white')
ax.text(bar_x[0], Ea_total + 0.06,
        f'Total: {Ea_total:.2f} eV\n({Ea_total * kJ_per_eV:.0f} kJ/mol)',
        ha='center', va='bottom', fontsize=12, fontweight='bold', color='#E6EDF3')

ax.text(bar_x[1], Ea_expt / 2,
        f'{Ea_expt:.2f} eV\n({Ea_expt * kJ_per_eV:.0f} kJ/mol)',
        ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# ── Discrepancy annotation ──
pct_diff = (Ea_total - Ea_expt) / Ea_expt * 100
ax.annotate(
    f'Δ = {Ea_total - Ea_expt:.2f} eV ({pct_diff:.0f}%)',
    xy=(0.6, Ea_expt), xytext=(0.6, Ea_expt + 0.2),
    fontsize=10, color='#8B949E', ha='center',
    arrowprops=dict(arrowstyle='-', color='#8B949E', lw=1, ls='--'),
)

ax.set_xticks(bar_x)
ax.set_xticklabels(['This Work\n(DFT-PBE)', 'Experimental\n(~240 kJ/mol)'],
                    fontsize=12, fontweight='bold')
ax.set_ylabel('Activation Energy (eV)', fontsize=13)
ax.set_title(
    'Ni Diffusion Activation Energy in BCC Fe\n'
    '$E_a^{diff} = E_f^{v} + E_a^{mig}$',
    fontsize=14, fontweight='bold', color='#E6EDF3',
)
ax.legend(loc='upper right', fontsize=10,
          facecolor='#161B22', edgecolor='#30363D', labelcolor='#E6EDF3')
ax.set_ylim(0, 3.3)
ax.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('figures/energy_decomposition.png', dpi=200, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print('Saved figures/energy_decomposition.png')
plt.close()
