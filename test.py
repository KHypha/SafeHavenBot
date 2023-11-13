import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('credentials.db')

# Create a cursor
cursor = conn.cursor()

# Execute a SQL query to check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_credentials'")

# Fetch the result
result = cursor.fetchone()

# Close the connection
conn.close()

# Check if the table exists
if result:
    print("The 'user_credentials' table exists in the database.")
else:
    print("The 'user_credentials' table does not exist in the database.")
