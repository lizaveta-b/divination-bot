import sqlite3
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

sentiment_pipeline = pipeline(
    'sentiment-analysis',
    model='blanchefort/rubert-base-cased-sentiment',
    tokenizer='blanchefort/rubert-base-cased-sentiment'
)

model_name = 'seara/rubert-tiny2-russian-emotion-detection-ru-go-emotions'

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

emotion_pipeline = pipeline(
    'text-classification',
    model=model,
    tokenizer=tokenizer,
    top_k=None)

emotions_rus = {
    'admiration': 'восхищение',
    'amusement': 'веселье',
    'anger': 'злость',
    'annoyance': 'раздражение',
    'approval': 'одобрение',
    'caring': 'заботу',
    'confusion': 'непонимание',
    'curiosity': 'любопытство',
    'desire': 'желание',
    'disappointment': 'разочарование',
    'disapproval': 'неодобрение',
    'disgust': 'отвращение',
    'embarrassment': 'смущение',
    'excitement': 'возбуждение',
    'fear': 'страх',
    'gratitude': 'признательность',
    'grief': 'горе',
    'joy': 'радость',
    'love': 'любовь',
    'nervousness': 'нервозность',
    'optimism': 'оптимизм',
    'pride': 'гордость',
    'realization': 'осознание',
    'relief': 'облегчение',
    'remorse': 'раскаяние',
    'sadness': 'грусть',
    'surprise': 'удивление',
    'neutral': 'нейтральность'
}


def av_score(user_id: int, current_score: float) -> str:
    '''
    Сравнивает тональность текущего предсказания с предыдущими.

    Параметр:
        user_id(int): Идентификатор пользователя
        current_score(float): Тональность текущего предсказания

    Возвращает строку со статистикой сравнения.
    '''
    con = sqlite3.connect('divinations.db')
    df = pd.read_sql_query(
        "SELECT score FROM Predictions WHERE user_id = ?",
        con,
        params=(user_id,))
    con.close()

    if df.empty:
        return 'У вас пока нет предыдущих предсказаний.'

    mean_score = df['score'].mean()

    if mean_score == current_score:
        msg1 = 'Тональность этого предсказания совпадает со средней тональностью ваших предсказаний.'
    else:
        if mean_score < current_score:
            change = 'позитивнее'
        else:
            change = 'негативнее'

        diff = round(abs(mean_score - current_score) * 100 / 2)
        msg1 = f'Это предсказание на {diff}% {change}, чем ваши предыдущие.'

    worse = (df['score'] < current_score).sum()
    total = len(df)
    prc = round(worse / total * 100)

    if worse > total / 2:
        msg2 = f'Это предсказание позитивнее, чем {prc}% ваших предсказаний.
    elif worse < total / 2:
        msg2 = f'Это предсказание негативнее, чем {100 - prc}% ваших предсказаний.'
    else:
        msg2 = f'Тональность вашего предсказания совпадает с медианой предыдущих предсказаний.'
    return msg1 + '\n' + msg2

def save_sent_stats(user_id: int, text: str) -> Dict[str, Union[str, float]]:
    '''
    Анализирует тональность и эмоции текста, сохраняет статистику.

    Параметр:
        user_id(int): Идентификатор пользователя
        text(str): Текст предсказания

    Возвращает словарь с текстом результата.
    '''
    tone = sentiment_pipeline(text)[0]

    if tone['label'] == 'NEGATIVE':
        tone_label = 'негативное'
    elif tone['label'] == 'POSITIVE':
        tone_label = 'позитивное'
    else:
        tone_label = 'нейтральное'

    tone_score = round(tone['score'] * 100)

    results = emotion_pipeline(text)[0]
    top_5 = sorted(results, key=lambda x: x['score'], reverse=True)

    emotions = []
    for emotion in top_5:
        if emotion['label'] == 'neutral':
            continue

        label_rus = emotions_rus.get(emotion['label'], emotion['label'])
        emotions.append(label_rus)

        if len(emotions) == 5:
            break

    current_score = tone['score']
    stat_text = av_score(user_id, current_score)

    result_text = (
        f'Это {tone_label} предсказание. Мы уверены в этом на {tone_score}%.\n'
        f'Ваше предсказание несёт {', '.join(emotions)}.\n'
        f'{stat_text}'
    )

    return {
        "text": result_text,
        "score": current_score
    }
