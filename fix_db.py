import sqlite3

conn = sqlite3.connect('driverex.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE cars ADD COLUMN image_url TEXT')
    conn.commit()
    print("✅ image_url column added successfully!")
except Exception as e:
    print(f"Note: {e}")

conn.close()