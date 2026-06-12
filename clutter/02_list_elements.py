from pycalphad import Database
from tinydb import where
from itertools import combinations

db = Database("COST507-modified.tdb")

TARGET = {'FE', 'NI', 'CO', 'MO', 'TI', 'AL'}
db_elements = db.elements - {'VA', '/-'}  # /-  is a cost507 artefact

print("=" * 50)
print("DB elements:", sorted(db_elements))
print("Our elements:", sorted(TARGET))
missing = sorted(TARGET - db_elements)
print("Missing from DB:", missing if missing else "None")
print("=" * 50)

# collect interactions using correct tinydb API
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
        if len(species) >= 2:
            interactions.add(frozenset(species))

unary   = [i for i in interactions if len(i) == 1 and i.issubset(TARGET)]
binary  = [i for i in interactions if len(i) == 2 and i.issubset(TARGET)]
ternary = [i for i in interactions if len(i) == 3 and i.issubset(TARGET)]
higher  = [i for i in interactions if len(i) >  3 and i.issubset(TARGET)]

print("\n--- UNARY (relevant) ---")
for i in sorted([tuple(sorted(x)) for x in unary]):
    print(" ", i)

print("\n--- BINARY (relevant) ---")
for i in sorted([tuple(sorted(x)) for x in binary]):
    print(" ", i)

print("\n--- TERNARY (relevant) ---")
for i in sorted([tuple(sorted(x)) for x in ternary]):
    print(" ", i)

if higher:
    print("\n--- HIGHER ORDER (relevant) ---")
    for i in sorted([tuple(sorted(x)) for x in higher]):
        print(" ", i)

# which needed pairs/triples are MISSING
found_bin = set(frozenset(x) for x in binary)
found_ter = set(frozenset(x) for x in ternary)

missing_bin = [tuple(sorted(x)) for x in
               [frozenset(p) for p in combinations(TARGET, 2)]
               if x not in found_bin]
missing_ter = [tuple(sorted(x)) for x in
               [frozenset(p) for p in combinations(TARGET, 3)]
               if x not in found_ter]

print("\n--- MISSING BINARIES ---")
for x in sorted(missing_bin):
    print(" ", x)

print("\n--- MISSING TERNARIES ---")
for x in sorted(missing_ter):
    print(" ", x)

print("\n--- ALL PHASES IN DB ---")
for p in sorted(db.phases.keys()):
    print(" ", p)