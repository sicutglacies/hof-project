import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

DATA_PATH = Path('../data/')
NUM_CLUSTERS = 5

model = SentenceTransformer('all-MiniLM-L12-v2')

with open(DATA_PATH / 'NLP.json') as f:
    data = json.load(f)

titles = list(map(lambda x: x['title'], data))
titles_embeddings = model.encode(titles, batch_size=16, show_progress_bar=True, convert_to_tensor=True)

clustering_model = KMeans(n_clusters=NUM_CLUSTERS)
clustering_model.fit(titles_embeddings)
cluster_assignment = clustering_model.labels_

clustered_sentences = {f'cluster_{i}': [] for i in range(NUM_CLUSTERS)}
for sentence_id, cluster_id in enumerate(cluster_assignment):
    clustered_sentences[f'cluster_{cluster_id}'].append(titles[sentence_id])

with open(DATA_PATH / 'relations' / 'clustered.json', 'w') as f:
    json.dump(clustered_sentences, f, indent=4)
