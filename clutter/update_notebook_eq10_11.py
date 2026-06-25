import json

file_path = "notebooks/li_et_al_2024/2.strength_model.ipynb"

with open(file_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            # Change 1: Eq 10 (order strengthening)
            if "sigma_os = M * (gamma_apb / (2 * b)) * np.sqrt(3 * np.pi * f / 8)" in line:
                line = line.replace(
                    "sigma_os = M * (gamma_apb / (2 * b)) * np.sqrt(3 * np.pi * f / 8)",
                    "sigma_os = M * (gamma_apb**1.5 / b) * np.sqrt(4 * rs * f / (np.pi * Gamma))"
                )
            
            # Change 2: Eq 11 (Orowan bypassing)
            if "sigma_or_MPa = sigma_or / 1e6" in line:
                # Add the alternate Eq 11 computation right after this line
                addition = (
                    "\n# Alternate form with f inside the log (per paper's printed Eq 11).\n"
                    "# NOTE: with this dataset's f and rs, the log argument (2*rs*f/b) is\n"
                    "# less than 1, making ln(...) negative and sigma_or_alt physically\n"
                    "# invalid as a strengthening value. This is likely because Ni3Ti's\n"
                    "# measured radius (1.8 nm) is well below its critical radius for\n"
                    "# Orowan bypassing (paper reports 5.37 nm), so the Orowan mechanism\n"
                    "# — and this formula — may not be meant to be evaluated at Ni3Ti's\n"
                    "# actual precipitate size. Kept here for transparency, NOT used in\n"
                    "# the shearing-vs-Orowan comparison below.\n"
                    "log_arg_alt = 2 * rs * f / b\n"
                    "sigma_or_alt = M * (0.4 * G * b) / (np.pi * np.sqrt(1 - v)) * np.log(log_arg_alt) / L\n"
                    "sigma_or_alt_MPa = sigma_or_alt / 1e6\n"
                    "print(f\"\\nΔσ_Orowan (f-in-log form) = {sigma_or_alt_MPa:.1f} MPa  \"\n"
                    "      f\"[log argument = {log_arg_alt:.3f}, \"\n"
                    "      f\"{'INVALID: negative result' if log_arg_alt < 1 else 'valid'}]\")\n"
                )
                line = line + addition
            
            new_source.append(line)
        cell["source"] = new_source

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
