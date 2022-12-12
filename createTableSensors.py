import sqlite3 as lite
import sys

con = lite.connect('sensorsData.db')

with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS SENSOR1data") 
    cur.execute("DROP TABLE IF EXISTS SENSOR2data") 
    cur.execute("CREATE TABLE SENSOR1data(timestamp DATETIME, ldr NUMERIC, accx NUMERIC, accy NUMERIC, accz NUMERIC, gyrx NUMERIC, gyry NUMERIC, gyrz NUMERIC, magx NUMERIC, magy NUMERIC, magz NUMERIC)")
    cur.execute("CREATE TABLE SENSOR2data(timestamp DATETIME, pres NUMERIC, temp NUMERIC)") 

