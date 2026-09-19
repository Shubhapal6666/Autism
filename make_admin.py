import sqlite3

conn = sqlite3.connect('autism.db')
conn.execute("UPDATE users SET is_admin = 1 WHERE email = 'avikdasiitkharagpur@gmail.com'")
conn.commit()
conn.close()
print("Done! You are now admin.")