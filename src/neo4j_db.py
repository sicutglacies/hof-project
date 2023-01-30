import json
from pathlib import Path
from spacy_application import LANGUAGES, TOPICS, METRICS
from neo4j_classes import Publication, Author, Language, Topic, Metric, Cluster, Affiliation


DATA_PATH = Path('../data/')

PUBLICATION_NODES = {}
AUTHOR_NODES = {}
LANGUAGE_NODES = {}
TOPIC_NODES = {}
METRIC_NODES = {}
CLUSTER_NODES = {}
AFFILIATION_NODES = {}


with open(DATA_PATH / 'NLP.json') as f:
    data = json.load(f)

with open(DATA_PATH / 'relations' / 'clustered.json') as f:
    clustered = json.load(f)

with open(DATA_PATH / 'relations' / 'spacy.json') as f:
    spacy_res = json.load(f)

# Creating Languages
for lang in LANGUAGES:
    lang_node = Language(
        name = lang
    ).save()
    LANGUAGE_NODES[lang] = lang_node

# Creating Topics
for topic in TOPICS:
    topic_node = Topic(
        name = topic
    ).save()
    TOPIC_NODES[topic] = topic_node

# Creating Metrics
for metric in METRICS:
    metric_node = Metric(
        name = metric
    ).save()
    METRIC_NODES[metric] = metric_node

# Creating Affiliations
for pub in data:
    for author in pub['authors']:
        if 'affiliations' in author.keys() and author['affiliations'] is not None and len(author['affiliations']) != 0:
            for aff in author['affiliations']:
                if aff not in AFFILIATION_NODES.keys():
                    aff_node = Affiliation(
                        name = aff
                    ).save()
                    AFFILIATION_NODES[aff] = aff_node

# Creating Publications
for pub, sp in zip(data, spacy_res):
    pub_node = Publication(
        link = pub['url'],
        title = pub['title'],
        abstract = pub['abstract'],
        publish_date = pub['publish_date'],
        conference = pub['conference']
    ).save()
    PUBLICATION_NODES[pub['title']] = pub_node

    if len(sp['languages']) != 0:
        for lang in sp['languages']:
            pub_node.language.connect(LANGUAGE_NODES[lang])

    if len(sp['topics']) != 0:
        for topic in sp['topics']:
            pub_node.topic.connect(TOPIC_NODES[topic])

    if len(sp['metrics']) != 0:
        for metric in sp['metrics']:
            pub_node.metric.connect(METRIC_NODES[metric])

# Creating Clusters
for n in range(5):
    cl_name = f'cluster_{n}'
    cluster_node = Cluster(
        name = cl_name
    ).save()
    CLUSTER_NODES[cl_name] = cluster_node
    for title in clustered[cl_name]:
        PUBLICATION_NODES[title].cluster.connect(cluster_node)

# Creating Authors
for pub in data:
    for author in pub['authors']:
        citations_count = author['Citation count'] if 'Citation count' in author.keys() else None
        pub_count = author['Publication counts'] if 'Publication counts' in author.keys() else None
        downloads_12m = author['Downloads (12 months)'] if 'Downloads (12 months)' in author.keys() else None
        downloads_all = author['Downloads (cumulative)'] if 'Downloads (cumulative)' in author.keys() else None

        author_node = Author(
            link = author['link'],
            name = author['name'],
            publication_count = pub_count,
            citation_count = citations_count,
            downloads_12_month = downloads_12m,
            downloads_cumulative = downloads_all
        ).save()
        PUBLICATION_NODES[pub['title']].author.connect(author_node)
        if 'affiliations' in author.keys() and author['affiliations'] is not None and len(author['affiliations']) != 0:
            for aff in author['affiliations']:
                author_node.affiliation.connect(AFFILIATION_NODES[aff])
