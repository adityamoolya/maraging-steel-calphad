# VPS DFT Input Review

## Verdict

These files are safe to run on the Azure VPS from a system-safety point of view. They are plain Quantum ESPRESSO input files, not shell scripts, and they contain no destructive commands, sudo usage, downloads, credential handling, or filesystem deletion.

They are not fully safe to treat as final scientific proof without checking convergence and documenting limitations. Run them only as fixed-cell SCF calculations unless you intentionally convert them back to relax calculations.

## Files Reviewed

- `fe54_pure.scf.in`
- `fe54_3ni_dispersed.scf.in`
- `fe54_3ni_clustered.scf.in`
- `fe54_5mo_dispersed.scf.in`
- `fe54_5mo_clustered.scf.in`

## Checks That Passed

- All five files declare `calculation = 'scf'`.
- All five files declare `nat = 54` and contain exactly 54 atomic positions.
- Composition counts are internally consistent:
  - `fe54_pure.scf.in`: 54 Fe
  - `fe54_3ni_dispersed.scf.in`: 51 Fe + 3 Ni
  - `fe54_3ni_clustered.scf.in`: 51 Fe + 3 Ni
  - `fe54_5mo_dispersed.scf.in`: 49 Fe + 5 Mo
  - `fe54_5mo_clustered.scf.in`: 49 Fe + 5 Mo
- `ntyp` values match the listed species.
- Pseudopotential filenames are consistent with the repository's `dft/pseudo/` directory:
  - `Fe.pbe-spn-rrkjus_psl.1.0.0.UPF`
  - `Ni.pbe-spn-rrkjus_psl.1.0.0.UPF`
  - `Mo.pbe-spn-rrkjus_psl.1.0.0.UPF`
- If run from `dft/vps`, `pseudo_dir = '../pseudo/'` points to the correct repository location.
- The Ni pseudopotential uses the corrected PSL family, avoiding the earlier mismatch with `Ni.pbe-nd-rrkjus.UPF`.

## Corrections / Cautions

1. These are SCF inputs, not relaxation inputs.

   The older `dft/fe54_*` files were `calculation = 'relax'`, while the VPS versions are `calculation = 'scf'`. This is acceptable for a quick fixed-lattice clustered-vs-dispersed comparison, but the energies should be described as unrelaxed fixed-cell SCF energies. Do not call them fully relaxed formation energies.

2. The model omits Co, Cr, Ti, Al, Si, and C.

   The assigned Li et al. composition is Fe-11Cr-4Co-8Ni-0.5Ti-5Mo-0.1Si-0.002C wt.%. These inputs only test Fe-Ni and Fe-Mo substitutional supercells. That can support a limited qualitative discussion of Ni/Mo clustering, but it does not reproduce the full alloy.

3. No Cr clustered/dispersed case is present.

   CODEX.md says the professor-relevant DFT target is clustered vs dispersed formation energies for Ni, Mo, and Cr in Fe-Co-X supercells. The VPS folder currently covers Ni and Mo only.

4. There is no Fe-Co base supercell.

   The paper target mentions Fe-Co-X supercells, but these files use Fe-X only. If the professor expects direct Fig. 8c-style replication, this is a scientific gap.

5. A pure Fe baseline exists, but reference-energy handling still needs care.

   The pure Fe input can provide a same-cell baseline, but formation/binding energy calculations also need consistent elemental references and a clearly stated formula. Do not mix old outputs from different pseudopotential families or different convergence settings.

6. Convergence is not guaranteed.

   Existing local `dft/fe54_*.out` attempts did not converge meaningfully. On the VPS, check every output for `JOB DONE`, final total energy, and absence of `convergence NOT achieved` before using the numbers.

7. The k-point and cutoff settings are plausible but not convergence-tested here.

   `ecutwfc = 45`, `ecutrho = 360`, and `K_POINTS 3 3 3` are reasonable starting values for these pseudopotentials, but a real report should state that convergence testing was limited unless you run cutoff/k-point checks.

## Recommended Run Command

From the repository root:

```bash
cd dft/vps
mkdir -p outdir
mpirun -np 4 pw.x -in fe54_pure.scf.in > fe54_pure.scf.out
mpirun -np 4 pw.x -in fe54_3ni_dispersed.scf.in > fe54_3ni_dispersed.scf.out
mpirun -np 4 pw.x -in fe54_3ni_clustered.scf.in > fe54_3ni_clustered.scf.out
mpirun -np 4 pw.x -in fe54_5mo_dispersed.scf.in > fe54_5mo_dispersed.scf.out
mpirun -np 4 pw.x -in fe54_5mo_clustered.scf.in > fe54_5mo_clustered.scf.out
```

For a 4 CPU / 32 GB VPS, `-np 4` is reasonable. Do not run as root unless your QE installation specifically requires it, which it normally should not.

## Output Validation Checklist

After each run:

```bash
grep -E "JOB DONE|convergence NOT achieved|!    total energy|estimated scf accuracy" *.out
```

Use only outputs that show normal completion and converged final energies.

## Final Recommendation

It is okay to push these files, clone on the VPS, and run them from `dft/vps`.

The main mistake to avoid is overclaiming. These inputs are acceptable for a limited, fixed-lattice SCF comparison of clustered vs dispersed Ni/Mo substitutions in Fe. They are not enough by themselves to claim full replication of the professor's assigned Li et al. DFT result.
