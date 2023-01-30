import json
import spacy
from pathlib import Path

DATA_PATH = Path('../data/')

LANGUAGES = [
    'English', 'Chinese', 'Spanish', 'Hindi', 'Bengali', 'Portuguese', 'Russian', 
    'Japanese', 'Vietnamese', 'German', 'French', 'Turkish', 'Korean', 'Italian',
    'Polish', 'Dutch', 'Indonesian', 'Thai', 'Danish', 'Czech', 'Finnish', 'Greek',
    'Swedish', 'Hungarian', 'Latvian', 'Lithuanian', 'Estonian', 'Arabic', 'Multilingual'
]

METRICS = [
    'Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC', 'MRR', 'MAP', 'RMSE', 'MAPE',
    'BLEU', 'METEOR', 'ROUGE', 'Perplexity'

]

TOPICS = [
    'Art', 'Biology', 'Business', 'Chemistry', 'Computer Science', 'Economics',
    'Engineering', 'Environmental Science', 'Geography', 'Geology', 'History',
    'Materials Science', 'Mathematics', 'Medicine', 'Philosophy', 'Physics',
    'Political Science', 'Psychology', 'Sociology'
]

TOPICS = list(map(lambda x: x.lower(), TOPICS))
METRICS = list(map(lambda x: x.lower(), METRICS))

if __name__ == '__main__':
    with open(DATA_PATH / 'NLP.json') as f:
        data = json.load(f)
        
    titles = list(map(lambda x: x['title'], data))
    abstracts = list(map(lambda x: x['abstract'], data))

    nlp = spacy.load("en_core_web_sm")

    spacy_results = []

    for abstract, title in zip(abstracts, titles):
        qualities = {
            'title': title,
            'languages': [],
            'topics': [],
            'metrics': []
        }
        doc = nlp(title + abstract)
        for token in doc:
            if token.text in LANGUAGES:
                qualities['languages'].append(token.text)
            if token.text.lower() in TOPICS:
                qualities['topics'].append(token.text.lower())
            if token.text.lower() in METRICS:
                qualities['metrics'].append(token.text.lower())
                
        qualities['topics'] = list(set(qualities['topics']))
        qualities['metrics'] = list(set(qualities['metrics']))
        qualities['languages'] = list(set(qualities['languages']))
        spacy_results.append(qualities)

    with open(DATA_PATH / 'relations' / 'spacy.json', 'w') as f:
        json.dump(spacy_results, f, indent=4)
