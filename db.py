import sqlite3

con = sqlite3.connect("ilo-prism-cache.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS dataflows(region, dataflow)")

res = cur.execute("SELECT * FROM dataflows")
con.commit()

print(res.fetchall())


con.close()
