# hof-project
NLU Deep Learning task
## Requirements: 
- geos

# Launch
1. poetry install
2. python -m spacy download en_core_web_sm
3. cd src/
4. python parse.py -> generates NLP.json, NLP_links.json in data/ folder
5. python clustering.py -> generates clustered.json in data/relations/ folder
6. python spacy_application -> generates spacy.json in data/relations/ folder
7. python neo4j_db.py -> generates nodes and connections
