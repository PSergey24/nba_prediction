import sqlite3

connection = sqlite3.connect('data/db/nba.db')


with open('data/db/schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

connection.commit()
connection.close()
