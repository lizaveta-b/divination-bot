import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

sw = set(stopwords.words('russian'))
morph = MorphAnalyzer()

def lemmatize_text(full_text):
    tokens = word_tokenize(full_text, language='russian')
    words = [w.lower() for w in tokens if w.isalpha()]
    no_sw = [w for w in words if w not in sw]
    lemmas = []
    for word in no_sw:
        lemma = morph.parse(word)[0].normal_form
        lemmas.append(lemma)
    return lemmas