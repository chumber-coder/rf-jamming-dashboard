import sqlite3

def init_db():
    conn = sqlite3.connect("rf_events.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        frequency REAL,
        peak_power REAL,
        bandwidth REAL,
        iq_path TEXT,
        tag TEXT
    )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
