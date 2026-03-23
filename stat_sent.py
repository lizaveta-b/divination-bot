import pandas as pd
import sqlite3

def av_score(user_id, current_score):
    con = sqlite3.connect('divinations.db')
    pred_df = pd.read_sql_query("SELECT * FROM Predictions WHERE user_id = ?", con, params=(user_id,))
    con.close()
    if pred_df.empty:
        print("Нет предыдущих предсказаний")
        return
    user_pred_df = pred_df.dropna()
    mean_score = user_pred_df['score'].mean()
    if mean_score == current_score:
        print('Тональность данного предсказания такая же, как средняя тональность предыдущих предсказаний.')
    else:
        if mean_score < current_score:
            change = 'позитивнее'
        else:
            change = 'негативнее'
        print(f'Тональность этого предсказания на {round(abs(mean_score - current_score) * 100 / 2)}% {change}, чем средняя тональность ваших предыдущих предсказаний.\n')
    scores = user_pred_df['score']
    worse = (scores < current_score).sum()
    total = len(scores)
    prc = round(worse / total * 100)
    if worse > total / 2:
        print(f"Данное предсказание позитивнее, чем {prc}% ваших предыдущих предсказаний!")
    elif worse < total / 2:
        print(f"Данное предсказание негативнее, чем {100 - prc}% ваших предыдущих предсказаний.")
    else:
        print("Данное предсказание по тональности находится на уровне медианы ваших предыдущих предсказаний.")