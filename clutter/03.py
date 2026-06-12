from pycalphad import Database
from tinydb import where
from itertools import combinations

db = Database("/home/adi/Downloads/mc_fecocrnbti.tdb")

TARGET = {'FE', 'NI', 'CO', 'MO', 'TI', 'AL'}
db_elements = db.elements - {'VA', '/-'}

print("=" * 50)
print("DB elements:", sorted(db_elements))
print("Our elements:", sorted(TARGET))
missing = sorted(TARGET - db_elements)
print("Missing from DB:", missing if missing else "None")
print("=" * 50)

# collect ALL interactions
interactions = set()
for phase_name in db.phases.keys():
    results = db._parameters.search(where('phase_name') == phase_name)
    for param in results:
        species = set()
        for subl in param['constituent_array']:
            for sp in subl:
                el = str(sp).split(':')[0].upper()
                if el != 'VA':
                    species.add(el)
        if len(species) >= 1:
            interactions.add(frozenset(species))

unary   = sorted([tuple(sorted(x)) for x in interactions if len(x) == 1])
binary  = sorted([tuple(sorted(x)) for x in interactions if len(x) == 2])
ternary = sorted([tuple(sorted(x)) for x in interactions if len(x) == 3])
higher  = sorted([tuple(sorted(x)) for x in interactions if len(x) >  3])

def mark(t):
    # mark as [OUR] if all elements are in TARGET
    return " [OUR]" if set(t).issubset(TARGET) else ""

print(f"\n--- UNARY ({len(unary)}) ---")
for i in unary:
    print(f"  {i}{mark(i)}")

print(f"\n--- BINARY ({len(binary)}) ---")
for i in binary:
    print(f"  {i}{mark(i)}")

print(f"\n--- TERNARY ({len(ternary)}) ---")
for i in ternary:
    print(f"  {i}{mark(i)}")

if higher:
    print(f"\n--- HIGHER ORDER ({len(higher)}) ---")
    for i in higher:
        print(f"  {i}{mark(i)}")

# summary of our coverage
found_bin = set(frozenset(x) for x in binary)
found_ter = set(frozenset(x) for x in ternary)

needed_bin = [frozenset(p) for p in combinations(TARGET, 2)]
needed_ter = [frozenset(p) for p in combinations(TARGET, 3)]

missing_bin = sorted([tuple(sorted(x)) for x in needed_bin if x not in found_bin])
missing_ter = sorted([tuple(sorted(x)) for x in needed_ter if x not in found_ter])

print("\n" + "=" * 50)
print("COVERAGE SUMMARY FOR OUR SYSTEM")
print("=" * 50)
print(f"Binaries  covered : {len(needed_bin) - len(missing_bin)}/{len(needed_bin)}")
print(f"Ternaries covered : {len(needed_ter) - len(missing_ter)}/{len(needed_ter)}")

print("\nMissing binaries:")
for x in missing_bin:
    print(f"  {x}")

print("\nMissing ternaries:")
for x in missing_ter:
    print(f"  {x}")

print("\n--- ALL PHASES IN DB ---")
for p in sorted(db.phases.keys()):
    print(f"  {p}")