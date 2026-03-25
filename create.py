import sqlite3

def create_db(db_path: str = "divinations.db")
    '''
    Создаёт базу данных. ER-диаграмма здесь: https://clck.ru/3SkKTf

    Параметр:
        db_path(str): путь к файлу базы данных
        
    Ничего не возвращает.
    '''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        text TEXT,
        words_n INTEGER,
        total_pages INTEGER DEFAULT 0
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pages (
        page_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        page_n INTEGER NOT NULL,
        total_lines INTEGER DEFAULT 0,
        FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
        UNIQUE(book_id, page_n)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Lines (
        line_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        line_n INTEGER NOT NULL,
        line_text TEXT,
        FOREIGN KEY (page_id) REFERENCES Pages(page_id) ON DELETE CASCADE,
        UNIQUE(page_id, line_n)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        line_id INTEGER,
        score REAL,
        prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (line_id) REFERENCES Lines(line_id) ON DELETE SET NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_book ON Pages(book_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lines_page ON Lines(page_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_book ON Predictions(book_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_user ON Predictions(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_line ON Predictions(line_id);")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db("divinations.db")
