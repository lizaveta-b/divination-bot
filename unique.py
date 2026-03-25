from collections import Counter
from lemmatize import lemmatize_text

def unique_prediction(pred: str, lemmas: List[str]) -> float:
    '''
    Рассчитывает уникальность предсказания относительно текста книги.

    Параметры:
        pred(str): Текст предсказания
        lemmas(List[str]): Список всех лемм книги

    Возвращает коэффициент уникальности (от 0 до 1).
    '''
    pred_lemmas = lemmatize_text(pred)
    if not pred_lemmas:
        return 0.0
    freq_dict = Counter(lemmas)
    total_len = len(lemmas)
    freq_sum = sum(freq_dict[w] / total_len for w in pred_lemmas)
    return freq_sum / len(pred_lemmas)
