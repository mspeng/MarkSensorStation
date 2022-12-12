import sqlite3 as lite
import sys

con = lite.connect('sensorsData.db')

with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS sensor1data") 
    cur.execute("DROP TABLE IF EXISTS sensor2data") 
    cur.execute("DROP TABLE IF EXISTS ldrdata") 
    cur.execute("DROP TABLE IF EXISTS accdata") 
    cur.execute("DROP TABLE IF EXISTS gyrdata") 
    cur.execute("DROP TABLE IF EXISTS magdata") 
    cur.execute("DROP TABLE IF EXISTS prsdata") 
    cur.execute("DROP TABLE IF EXISTS tmpdata") 
    cur.execute("CREATE TABLE ldrdata(timestamp DATETIME, ldr NUMERIC)")
    cur.execute("CREATE TABLE accdata(timestamp DATETIME, accx NUMERIC, accy NUMERIC, accz NUMERIC)")
    cur.execute("CREATE TABLE gyrdata(timestamp DATETIME, gyrx NUMERIC, gyry NUMERIC, gyrz NUMERIC)")
    cur.execute("CREATE TABLE magdata(timestamp DATETIME, magx NUMERIC, magy NUMERIC, magz NUMERIC)")
    cur.execute("CREATE TABLE prsdata(timestamp DATETIME, pres NUMERIC)") 
    cur.execute("CREATE TABLE tmpdata(timestamp DATETIME, temp NUMERIC)") 

