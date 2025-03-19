import pandas as pd
import psycopg2
import json


conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    dbname=DB_NAME
)
cursor = conn.cursor()

query = 'UPDATE topics SET issue_title = %s WHERE name = %s'

cursor.execute(query,("animal","Animals"))

conn.commit()

if cursor:
    cursor.close()

if conn:
    conn.close()
