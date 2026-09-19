import sqlite3

conn   = sqlite3.connect('autism.db')
cursor = conn.cursor()

print("Current users:")
cursor.execute("SELECT id, name, email, is_admin, is_verified FROM users")
users = cursor.fetchall()
for u in users:
    print(f"  ID:{u[0]} | {u[1]} | {u[2]} | admin:{u[3]} | verified:{u[4]}")

print()

# Make ALL existing users verified so they can login
conn.execute("UPDATE users SET is_verified = 1")
print("All users set to verified")

# Make the first account admin
conn.execute("UPDATE users SET is_admin = 1 WHERE id = 1")
print("ID 1 (Avik Das) set as admin")

conn.commit()

print()
print("Updated users:")
cursor.execute("SELECT id, name, email, is_admin, is_verified FROM users")
users = cursor.fetchall()
for u in users:
    print(f"  ID:{u[0]} | {u[1]} | {u[2]} | admin:{u[3]} | verified:{u[4]}")

conn.close()
print()
print("Done! All users can now login.")