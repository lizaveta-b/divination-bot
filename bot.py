import telebot
from telebot import types
import sqlite3

from context import find_sentence
from unique import unique_prediction
from sentiment import save_sent_stats
from sentiment import av_score
from similar import get_similar_words
from stats import all_stats

token = "bot token here"
bot = telebot.TeleBot(token)
db_path = "divinations.db"
user_state = {}

def get_or_create_user(telegram_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        cursor.execute(
            "INSERT INTO Users (telegram_id) VALUES (?)",
            (telegram_id,)
        )
        user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def save_prediction(user_id, book_id, score):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Predictions (book_id, user_id, score)
        VALUES (?, ?, ?)
    """, (book_id, user_id, score))
    conn.commit()
    conn.close()

def get_books():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title FROM Books")
    books = cursor.fetchall()
    conn.close()
    return books

def get_book_structure(book_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.page_n, l.line_n, l.line_text
        FROM Pages p
        JOIN Lines l ON p.page_id = l.page_id
        WHERE p.book_id = ?
        ORDER BY p.page_n, l.line_n
    """, (book_id,))
    rows = cursor.fetchall()
    conn.close()
    book = {}
    for page_n, line_n, text in rows:
        book.setdefault(page_n - 1, []).append(text)
    return book

def get_book_lemmas(book_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM Books WHERE book_id = ?", (book_id,))
    lemmas = cursor.fetchone()[0]
    conn.close()
    return lemmas.split()

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Получить предсказание", "Общая статистика")
    bot.send_message(chat_id, "Готовы получить предсказание?", reply_markup=markup)

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Назад")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "Общая статистика")
def handle_stats(message):
    chat_id = message.chat.id
    user_id = get_or_create_user(chat_id)
    text_result, plot_buf = all_stats(user_id)
    bot.send_message(chat_id, text_result)
    if plot_buf:
        bot.send_photo(chat_id, plot_buf)
    else:
        bot.send_message(chat_id, "К сожалению, нам пока недостаточно данных для графика")

@bot.message_handler(func=lambda m: m.text == "Получить предсказание")
def ask_question(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Я придумал вопрос", "Назад")
    bot.send_message(message.chat.id, "Придумайте вопрос:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Я придумал вопрос")
def choose_book(message):
    books = get_books()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for _, title in books:
        markup.add(title)
    markup.add("Назад")
    user_state[message.chat.id] = {}
    bot.send_message(message.chat.id, "Выберите книгу:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handler(message):
    chat_id = message.chat.id
    text = message.text
    if text == "Назад":
        user_state.pop(chat_id, None)
        main_menu(chat_id)
        return
    if chat_id not in user_state:
        return
    state = user_state[chat_id]
    if "user_id" not in state:
        state["user_id"] = get_or_create_user(chat_id)
    if "book_id" not in state:
        for book_id, title in get_books():
            if text == title:
                state["book_id"] = book_id
                state["book"] = get_book_structure(book_id)
                bot.send_message(
                    chat_id,
                    f"В книге {len(state['book'])} страниц. Введите номер страницы:",
                    reply_markup=back_button()
                )
                return
    if "page" not in state:
        if not text.isdigit():
            bot.send_message(chat_id, "Вы ввели что-то не то:( Введите просто число, входящее в диапазон:")
            return
        page = int(text)
        book = state["book"]
        if page < 1 or page > len(book):
            bot.send_message(chat_id, f"Введите номер страницы от 1 до {len(book)}")
            return
        state["page"] = page
        bot.send_message(
            chat_id,
            f"На этой странице {len(book[page - 1])} строк. Введите номер строки:",
            reply_markup=back_button()
        )
        return
    if "line" not in state:
        if not text.isdigit():
            bot.send_message(chat_id, "Вы ввели что-то не то:( Введите просто число, входящее в диапазон:")
            return
        line = int(text)
        book = state["book"]
        page = state["page"]
        if line < 1 or line > len(book[page - 1]):
            bot.send_message(chat_id, f"Введите номер строки от 1 до {len(book[page - 1])}")
            return
        state["line"] = line
        sentence = find_sentence(book, page, line)
        state["sentence"] = sentence
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Тональность", "Связанные слова")
        markup.add("Уникальность", "Ещё предсказание")
        markup.add("Назад")
        bot.send_message(
            chat_id,
            f'Книга говорит:\n\n"{sentence}"\n\nЧто вы хотите узнать о вашем предсказании?',
            reply_markup=markup
        )
        return
    sentence = state["sentence"]
    if text == "Тональность":
        result = save_sent_stats(state["user_id"], sentence)
        state["current_score"] = result["score"]
        save_prediction(state["user_id"], state["book_id"], result["score"])
        bot.send_message(chat_id, result["text"])
    elif text == "Связанные слова":
        sim = get_similar_words(sentence, top_n=5)
        words = [
            w["word"]
            for k in sim["similar_words"]
            for w in sim["similar_words"][k]
        ]
        bot.send_message(chat_id, ", ".join(words) or "К сожалению, мы ничего не нашли:(")
    elif text == "Уникальность":
        lemmas = get_book_lemmas(state["book_id"])
        score = unique_prediction(sentence, lemmas)
        bot.send_message(chat_id, f"Частотность вашего предсказания относительно всей книги: {round(score, 5)}")
    elif text == "Ещё предсказание":
        user_state.pop(chat_id)
        ask_question(message)

bot.polling()