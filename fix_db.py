import sqlite3

conn = sqlite3.connect('autism.db')

# Add missing columns one by one
# Each is wrapped in try/except so it skips if column already exists

try:
    conn.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
    print("Added is_admin column")
except Exception as e:
    print(f"is_admin already exists: {e}")

try:
    conn.execute('ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0')
    print("Added is_verified column")
except Exception as e:
    print(f"is_verified already exists: {e}")

try:
    conn.execute('ALTER TABLE users ADD COLUMN verify_token TEXT')
    print("Added verify_token column")
except Exception as e:
    print(f"verify_token already exists: {e}")

# Now set your account as admin AND verified
conn.execute("UPDATE users SET is_admin = 1, is_verified = 1 WHERE email = 'avikdasiitkharagpur@gmail.com'")
conn.commit()

# Confirm it worked
cursor = conn.cursor()
cursor.execute("SELECT id, name, email, is_admin, is_verified FROM users")
users = cursor.fetchall()

print("\nAll users in database:")
for u in users:
    print(f"  ID:{u[0]} | {u[1]} | {u[2]} | admin:{u[3]} | verified:{u[4]}")

conn.close()
print("\nDone! You are now admin and verified.")