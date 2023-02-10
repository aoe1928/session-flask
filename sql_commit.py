import sqlite3

DB = 'test.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# INSERT

for n in range(60):
    cur.execute(f'INSERT INTO diary VALUES ({n + 62}, "dream", "DREAM{n + 1}", 20220717)')

conn.commit()

cur.close()

conn.close()