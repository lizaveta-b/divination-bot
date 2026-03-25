import sqlite3
from create import create_db
from pdf_to_text import pdf_to_text
from lemmatize import lemmatize_text
from collections import Counter
from nltk.tokenize import word_tokenize

def insert_book(db_path: str, pdf_path: str, title: str, author: str) -> None:
    '''
    Добавляет из PDF-файла книгу в базу данных.

    Параметры:
        db_path(str): Путь к файлу базы данных
        pdf_path(str): Путь к PDF-файлу с книгой
        title(str): Название книги
        author(str): Автор книги
        
    Ничего не возвращает.
    '''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    data = pdf_to_text(pdf_path)
    total_pages = len(data)
    total_words = 0
    full_text = '\n'.join(
        line for page in data.values() for line in page
    )
    for lines in data.values():
        for line in lines:
            total_words += len(line.split())
    lemmas = lemmatize_text(full_text)
    lemmas_text = ' '.join(lemmas)
    cursor.execute("""
        INSERT INTO Books (title, author, text, words_n, total_pages)
        VALUES (?, ?, ?, ?, ?)
    """, (title, author, lemmas_text, total_words, total_pages))
    book_id = cursor.lastrowid
    for page_n, lines in data.items():
        cursor.execute("""
            INSERT INTO Pages (book_id, page_n, total_lines)
            VALUES (?, ?, ?)
        """, (book_id, page_n, len(lines)))
        page_id = cursor.lastrowid
        for i, line in enumerate(lines, start=1):
            cursor.execute("""
                INSERT INTO Lines (page_id, line_n, line_text)
                VALUES (?, ?, ?)
            """, (page_id, i, line))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_path = 'divinations.db'
    create_db(db_path)
    books = [
        ('daughter.pdf', 'Капитанская дочка', 'А. С. Пушкин'),
        ('bible.pdf', 'Библия', ''),
        ('jokes.pdf', 'Сборник анекдотов', ''),
        ('master.pdf', 'Мастер и Маргарита', 'М. А. Булгаков'),
        ('slovar.pdf', 'Толковый словарь Ожегова', 'С. И. Ожегов')
    ]
    for pdf, title, author in books:
        insert_book(db_path, pdf, title, author)
