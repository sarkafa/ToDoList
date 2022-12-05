import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO todo (id, text) VALUES ('Ukol 1', 'Dokonci_stage1')")

connection.commit()
connection.close()
