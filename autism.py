import sqlite3

conn   = sqlite3.connect('autism.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name, email, is_admin, is_verified, verify_token FROM users")
users = cursor.fetchall()

print("All users:")
for u in users:
    print(f"  ID:{u[0]} | Name:{u[1]} | Email:{u[2]} | admin:{u[3]} | verified:{u[4]} | token:{u[5]}")

conn.close()