import mysql.connector

try:
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # اكتب الباسورد إذا غيرته
        database="transport_system"
    )

    if con.is_connected():
        print("✅ MySQL Connection Successful")
        cur = con.cursor()
        cur.execute("SHOW TABLES;")
        tables = cur.fetchall()
        print("✅ Tables:", tables)

except mysql.connector.Error as err:
    print("❌ Error:", err)
