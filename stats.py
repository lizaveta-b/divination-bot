import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Tuple, Optional


def all_stats(user_id: int) -> Tuple[str, Optional[BytesIO]]:
    '''
    Формирует статистику по предсказаниям пользователя и общую статистику.

    Параметр:
        user_id(int): идентификатор пользователя

    Возвращает кортеж (статистика(str), BytesIO (это графики)).
    '''
    con = sqlite3.connect('divinations.db')
    query_user = '''
        SELECT b.title, COUNT(*) as cnt
        FROM Predictions p
        JOIN Books b ON p.book_id = b.book_id
        WHERE p.user_id = ?
        GROUP BY b.book_id
        ORDER BY cnt DESC
        LIMIT 5
    '''
    df_user = pd.read_sql_query(query_user, con, params=(user_id,))
    query_all = '''
        SELECT b.title, COUNT(*) as cnt
        FROM Predictions p
        JOIN Books b ON p.book_id = b.book_id
        GROUP BY b.book_id
        ORDER BY cnt DESC
        LIMIT 5
    '''
    df_all = pd.read_sql_query(query_all, con)
    df_scores = pd.read_sql_query('''
        SELECT p.user_id, u.telegram_id, p.score
        FROM Predictions p
        JOIN Users u ON p.user_id = u.user_id
    ''', con)
    con.close()
    messages = []
    if not df_user.empty:
        messages.append(
            f"Вы чаще всего выбирали '{df_user.iloc[0]['title']}' "
            f'({df_user.iloc[0]['cnt']} раз)'
        )
    if not df_all.empty:
        messages.append(
            f"Самая популярная книга среди пользователей: '{df_all.iloc[0]['title']}' "
            f"({df_all.iloc[0]['cnt']} раз)"
        )
    text_result = '\n'.join(messages) if messages else 'К сожалению, нам не хватает данных:('
    if df_scores.empty:
        return text_result, None
    fig, axes = plt.subplots(2, 2, figsize=(18, 16))
    if not df_user.empty:
        axes[0, 0].barh(df_user['title'], df_user['cnt'])
        axes[0, 0].set_title('Ваши книги')
    if not df_all.empty:
        axes[0, 1].barh(df_all['title'], df_all['cnt'])
        axes[0, 1].set_title('Книги, которые чаще всего выбирают')
    axes[1, 0].hist(df_scores['score'], bins=20)
    axes[1, 0].set_title('Распределение тональности по пользователям')
    user_stats = df_scores.groupby('user_id')['score'].mean()
    axes[1, 1].barh(user_stats.index.astype(str), user_stats.values)
    axes[1, 1].set_title('Средняя тональность по пользователям')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return text_result, buf
