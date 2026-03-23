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
    top_k=None
)

emotions_rus = {
    'admiration': 'восхищение',
    'amusement': 'веселье',
    'anger': 'злость',
    'annoyance': 'раздражение',
    'approval': 'одобрение',
    'caring': 'забота',
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

def analyze_text(text: str):
    tone = sentiment_pipeline(text)[0]
    if tone['label'] == 'NEGATIVE':
        tone_label = 'негативная'
    elif tone['label'] == 'POSITIVE':
        tone_label = 'позитивная'
    else:
        tone_label = 'нейтральная'
    tone_score = round(tone['score'] * 100)
    results = emotion_pipeline(text)[0]
    top_5 = sorted(results, key=lambda x: x['score'], reverse=True)
    emotions = []
    for emotion in top_5:
        if emotion['label'] == 'neutral':
            continue
        label_eng = emotion['label']
        label_rus = emotions_rus.get(label_eng, label_eng)
        emotions.append({
            'emotion': label_rus,
            'score': round(emotion['score'], 3)
        })
        if len(emotions) == 5:
            break
    return {
        'tone': tone_label,
        'tone_score': tone_score,
        'emotions': emotions
    }