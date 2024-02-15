from config import *
from indexing.rag_helper import LoadAndSplit,IndexConstructor

if "docs" in config_index.keys():
    search = IndexConstructor(**config_index)
else:
    docs = LoadAndSplit(**config_load_and_split)
    search=IndexConstructor(docs=docs,**config_index)

