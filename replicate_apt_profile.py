import numpy as np
import matplotlib.pyplot as plt
import os

# Ensure figures directory exists
os.makedirs('figures', exist_ok=True)

# Compositions from CALPHAD (at.%)
matrix_comp = {
    'Fe': 72.34, 'Cr': 12.02, 'Ni': 7.62, 'Mo': 4.42, 
    'Ti': 2.04, 'Co': 1.35, 'Si': 0.20
}

precipitate_comp = {
    'Fe': 1.58, 'Cr': 0.00, 'Ni': 73.43, 'Mo': 0.00, 
    'Ti': 24.98, 'Co': 0.00, 'Si': 0.00
}

# Distance array mimicking the APT data (d1)
x = np.linspace(0, 8, 15)

# Sigmoid transition centered at x=4
transition = 0.5 * (1 + np.tanh((x - 4) / 0.8))

# Define colors and markers to match the paper
style = {
    'Fe': {'color': 'orange', 'marker': 's'},
    'Co': {'color': 'saddlebrown', 'marker': 'o'},
    'Ni': {'color': 'limegreen', 'marker': 's'},
    'Ti': {'color': 'indigo', 'marker': 'd'},
    'Mo': {'color': 'red', 'marker': 'o'},
    'Cr': {'color': 'hotpink', 'marker': 'd'},
    'Si': {'color': 'blue', 'marker': '^'}
}

fig, ax = plt.subplots(figsize=(6, 5))

# Background colors
ax.axvspan(0, 4, facecolor='#fffae6', alpha=1.0) # Light yellow for Matrix
ax.axvspan(4, 8, facecolor='#e6ffe6', alpha=1.0) # Light green for Ni3Ti

# Phase labels
ax.text(1.5, 90, 'Matrix', ha='center', va='center', color='darkgoldenrod', fontsize=12)
ax.text(6.5, 90, 'Ni$_3$Ti', ha='center', va='center', color='green', fontsize=12)

# Plot lines
for element in matrix_comp.keys():
    y = matrix_comp[element] + (precipitate_comp[element] - matrix_comp[element]) * transition
    ax.plot(x, y, label=element, color=style[element]['color'], 
            marker=style[element]['marker'], markersize=5, linewidth=1.5)

# Formatting
ax.set_xlabel('Distance (nm)', fontsize=12)
ax.set_ylabel('Concentration (at. %)', fontsize=12)
ax.set_xlim(0, 8)
ax.set_ylim(-5, 100)

# Legend
ax.legend(loc='center left', bbox_to_anchor=(0.02, 0.45), frameon=False, fontsize=10)

# Top text mimicking the paper (d1)
top_text = f"{precipitate_comp['Fe']:.1f}Fe-{precipitate_comp['Co']:.1f}Co-{precipitate_comp['Ni']:.1f}Ni-{precipitate_comp['Ti']:.1f}Ti-{precipitate_comp['Mo']:.1f}Mo-{precipitate_comp['Cr']:.1f}Cr-{precipitate_comp['Si']:.1f}Si (CALPHAD)"
ax.text(4, 98, top_text, ha='center', va='top', color='green', fontsize=8)

# Panel label
ax.text(0.2, 95, '(d1) CALPHAD Replica', fontsize=11, fontweight='bold')

plt.tight_layout()
output_path = 'figures/replicated_apt_d1.png'
plt.savefig(output_path, dpi=300)
print(f'Figure saved to {output_path}')
