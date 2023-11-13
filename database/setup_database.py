import sqlite3

# Create an SQLite database and a table to store user credentials
def setup_database():
    conn = sqlite3.connect('credentials.db')
    cursor = conn.cursor()

    # Create a table to store user API credentials
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_credentials (
        user_id INTEGER PRIMARY KEY,
        api_key TEXT,
        api_secret TEXT
    )
    ''')
 # Create table for risk management parameters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_management (
            user_id INTEGER PRIMARY KEY,
            max_risk_percentage REAL,
            max_losses_per_day INTEGER,
            max_leverage INTEGER,
            daily_profit_target REAL
        )
    ''')

    conn.commit()
    conn.close()

# Call the setup_database function to initialize the database
setup_database()
