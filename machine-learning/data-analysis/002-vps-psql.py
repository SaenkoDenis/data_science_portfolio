import psycopg2

conn = psycopg2.connect(database="postgres", user='postgreadmin',
password='1234', host='188.123.456.768', port= '5432')
#Creating a cursor object using the cursor() method
cursor = conn.cursor()
#Executing an PostgreSQL function using the execute() method
cursor.execute("select version()")
# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print("Connection established to: ",data)
#Closing the connection
conn.close()

# Connection established to:  ('PostgreSQL 12.12
# (Ubuntu 12.12-0ubuntu0.20.04.1) on x86_64-pc-linux-gnu,
# compiled by gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0, 64-bit',)