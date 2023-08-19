import sqlite3 as lite
import sys

con = lite.connect('sensorsData.db')

with con:
    cur = con.cursor()
    cur.execute("INSERT INTO SENSOR1data VALUES(datetime('now'), 600, 50, -50, 1000, 0, 0, 0 , -28, 16, -70)")
    cur.execute("INSERT INTO SENSOR1data VALUES(datetime('now'), 500, 60, -60, 1000, 0, 0, 0 , -28, 16, -70)")
    cur.execute("INSERT INTO SENSOR1data VALUES(datetime('now'), 400, 70, -70, 1000, 0, 0, 0 , -28, 16, -70)")
    cur.execute("INSERT INTO SENSOR2data VALUES(datetime('now'), 1055.45, 30.5)")
    cur.execute("INSERT INTO SENSOR2data VALUES(datetime('now'), 1015.45, 32.5)")
    cur.execute("INSERT INTO SENSOR2data VALUES(datetime('now'), 1095.45, 34.5)")
