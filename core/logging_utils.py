import sqlite3

def log_event(frequency, power, bandwidth, iq_path=None, tag="unclassified"):
    conn = sqlite3.connect("rf_events.db")
    c = conn.cursor()
    c.execute('''INSERT INTO events (timestamp, frequency, peak_power, bandwidth, iq_path, tag)
                 VALUES (datetime('now'), ?, ?, ?, ?, ?)''',
              (frequency, power, bandwidth, iq_path, tag))
    conn.commit()
    conn.close()
