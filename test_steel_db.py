from pycalphad import Database

DB_PATH = '../databases/steel_database_fix.tdb'
db = Database(DB_PATH)

print(sorted(list(db.phases.keys())))

