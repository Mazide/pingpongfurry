import sqlite3

DATABASE = 'ping_pong.db'

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL DEFAULT 1000
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            winner_id INTEGER NOT NULL,
            loser_id INTEGER NOT NULL,
            FOREIGN KEY (winner_id) REFERENCES players (id),
            FOREIGN KEY (loser_id) REFERENCES players (id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
