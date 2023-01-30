from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, config


config.DATABASE_URL = 'bolt://neo4j:12345678@localhost:7687'

class Publication(StructuredNode):
    link = StringProperty(unique_index=True)
    title = StringProperty()
    abstract = StringProperty()
    publish_date = StringProperty()
    conference = StringProperty()
    language = RelationshipTo('Language', 'TRAINED-ON')
    metric = RelationshipTo('Metric', 'USES-METRIC')
    topic = RelationshipTo('Topic', 'ABOUT-TOPIC')
    cluster = RelationshipTo('Cluster', 'BELONGS-TO')
    author = RelationshipFrom('Author', 'WRITTEN-BY')

class Author(StructuredNode):
    link = StringProperty(unique_index=True)
    name = StringProperty()
    publication_count = StringProperty()
    citation_count = StringProperty()
    downloads_12_month = StringProperty()
    downloads_cumulative = StringProperty()
    affiliation = RelationshipTo('Affiliation', 'AFFILIATED-WITH')

class Language(StructuredNode):
    name = StringProperty(unique_index=True)

class Topic(StructuredNode):
    name = StringProperty(unique_index=True)

class Metric(StructuredNode):
    name = StringProperty(unique_index=True)

class Cluster(StructuredNode):
    name = StringProperty(unique_index=True)

class Affiliation(StructuredNode):
    name = StringProperty(unique_index=True)
