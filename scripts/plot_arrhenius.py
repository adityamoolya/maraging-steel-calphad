"""
Arrhenius extrapolation of Ni hop rate in BCC Fe.
Uses the converged CI-NEB migration barrier (Ea = 0.661 eV).

Generates: figures/arrhenius_ni_bcc_fe.png
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# ── Constants ──
Ea = 0.661          # eV, converged CI-NEB migration barrier
kB = 8.617e-5       # eV/K
T_ref = 200 + 273.15  # baseline temperature (K)

# ── Temperature range ──
T_C = np.linspace(200, 850, 500)
T_K = T_C + 273.15

# ── Arrhenius rate (normalised to 200 °C) ──
rate = np.exp(-Ea / (kB * T_K))
rate_ref = np.exp(-Ea / (kB * T_ref))
relative_rate = rate / rate_ref

# ── Key temperatures ──
highlights = {
    '450°C': (450 + 273.15, '#E07020'),
    '480°C (Li et al.)': (480 + 273.15, '#9B2D8B'),
}

# ── Styling ──
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'Helvetica Neue', 'Arial'],
    'font.size': 11,
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    f'Arrhenius Extrapolation of Ni Hop Rate in BCC Fe\n'
    f'$E_a$ = {Ea} eV  (CI-NEB, 7 images, converged)',
    fontsize=15, fontweight='bold', color='#E6EDF3', y=0.98,
)

# ═══════════════════════════════════════════
# Panel 1: Hop Rate vs Temperature
# ═══════════════════════════════════════════
ax1.semilogy(T_C, relative_rate, color='#58A6FF', linewidth=2.5, zorder=3)
ax1.set_xlabel('Temperature (°C)', fontsize=12)
ax1.set_ylabel('Relative Hop Rate (normalised to 200°C)', fontsize=12)
ax1.set_title('Hop Rate vs Temperature', fontsize=13, color='#58A6FF')
ax1.grid(True, alpha=0.3)

for label, (T_hi, color) in highlights.items():
    rate_hi = np.exp(-Ea / (kB * T_hi)) / rate_ref
    T_hi_C = T_hi - 273.15
    ax1.axvline(T_hi_C, color=color, linestyle='--', alpha=0.7, linewidth=1.5)
    ax1.plot(T_hi_C, rate_hi, 'o', color=color, markersize=10, zorder=5,
             markeredgecolor='white', markeredgewidth=1.5)
    ax1.annotate(
        f'{label.split(" ")[0]}\n{rate_hi:.1e}×',
        xy=(T_hi_C, rate_hi), xytext=(15, -20),
        textcoords='offset points', fontsize=9.5, color=color,
        fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=color, lw=1.2),
    )

ax1.legend(
    [plt.Line2D([], [], color=c, linestyle='--', lw=1.5) for _, (_, c) in highlights.items()],
    list(highlights.keys()),
    loc='upper left', fontsize=10,
    facecolor='#161B22', edgecolor='#30363D', labelcolor='#E6EDF3',
)

# ═══════════════════════════════════════════
# Panel 2: Classic Arrhenius (ln rate vs 1/T)
# ═══════════════════════════════════════════
inv_T = 1000.0 / T_K  # 1000/T in K⁻¹
ln_rate = -Ea / (kB * T_K)

ax2.plot(inv_T, ln_rate, color='#58A6FF', linewidth=2.5, zorder=3)
ax2.set_xlabel('1000/T  (K⁻¹)', fontsize=12)
ax2.set_ylabel('ln(rate) ∝ −$E_a$/$k_B T$', fontsize=12)
ax2.set_title('Arrhenius Plot  (ln rate vs 1/T)', fontsize=13, color='#58A6FF')
ax2.grid(True, alpha=0.3)

for label, (T_hi, color) in highlights.items():
    inv_T_hi = 1000.0 / T_hi
    ln_rate_hi = -Ea / (kB * T_hi)
    short = label.split(' ')[0]
    ax2.plot(inv_T_hi, ln_rate_hi, 'o', color=color, markersize=10, zorder=5,
             markeredgecolor='white', markeredgewidth=1.5)
    ax2.annotate(
        short, xy=(inv_T_hi, ln_rate_hi), xytext=(15, 10),
        textcoords='offset points', fontsize=10, color=color, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=color, lw=1.2),
    )

ax2.legend(
    [plt.Line2D([], [], marker='o', color=c, linestyle='None', markersize=8,
                markeredgecolor='white') for _, (_, c) in highlights.items()],
    [l.split(' ')[0] for l in highlights.keys()],
    loc='upper right', fontsize=10,
    facecolor='#161B22', edgecolor='#30363D', labelcolor='#E6EDF3',
)

plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig('figures/arrhenius_ni_bcc_fe.png', dpi=200, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print('Saved figures/arrhenius_ni_bcc_fe.png')
plt.close()
