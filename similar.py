from gensim.models import KeyedVectors
from keybert import KeyBERT
from russian_tagsets import converters
from pymorphy3 import MorphAnalyzer
from lemmatize import lemmatize_text
import zipfile
import os
import urllib.request

morph = MorphAnalyzer()
conv = converters.converter('opencorpora-int', 'ud20')

model_path = "model_185/model.bin"

if not os.path.exists(model_path):
    url = "https://vectors.nlpl.eu/repository/20/185.zip"
    urllib.request.urlretrieve(url, "185.zip")
    with zipfile.ZipFile('185.zip', 'r') as zip_ref:
        zip_ref.extractall('model_185')

model = KeyedVectors.load_word2vec_format(model_path, binary=True)
kw_model = KeyBERT('DeepPavlov/rubert-base-cased')
def add_pos_tags(words):
    result = []
    for word in words:
        parsed = morph.parse(word)[0]
        pos_tag = conv(str(parsed.tag)).split()[0]
        result.append(f"{word}_{pos_tag}")
    return result

def get_similar_words(text, top_n = 1, use_pos = True):
    keywords_info = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 1),
        top_n=1
    )
    keywords = [kw[0] for kw in keywords_info]
    if not keywords:
        return {
            'keywords': [],
            'similar_words': {}
        }
    lemmas = lemmatize_text(" ".join(keywords))
    if use_pos:
        processed_words = add_pos_tags(lemmas)
    else:
        processed_words = lemmas
    results = {}
    for word in processed_words:
        try:
            similar = model.most_similar(word, topn=top_n)
            cleaned = [
                {
                    'word': sim_word.split('_')[0],
                    'score': float(score)
                }
                for sim_word, score in similar
            ]
            results[word] = cleaned
        except:
            results[word] = []
    return {
        'keywords': keywords,
        'similar_words': results
    }