import sqlite3
import os

# Connect to the database
DB = os.path.join(os.path.dirname(__file__), "database.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Print schema
c.execute("SELECT sql FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for table in tables:
    print(table[0])
    print()

conn.close()