from typing import (
    Any,
    Union,
    List,
    Optional
)

import os
import glob
import json
from pathlib import Path

from langchain_community.document_loaders.directory import _is_visible, logger

from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings,GPT4AllEmbeddings,AzureOpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter,MarkdownHeaderTextSplitter
from langchain_community.document_loaders import TextLoader,PyPDFLoader,AzureAIDocumentIntelligenceLoader,DirectoryLoader
from langchain_community.vectorstores import ElasticsearchStore,FAISS,AzureSearch,Chroma

import inspect

class AzureDocIntelHat(AzureAIDocumentIntelligenceLoader):
    def __init__(self, file_path, **kwargs):
        super(AzureDocIntelHat, self).__init__(
            file_path=file_path, **kwargs)

loading_method_mapping={"PyPDFLoader":{"method":PyPDFLoader,
                         "directory":False},
                "AzureAIDocumentIntelligenceLoader":{"method":AzureDocIntelHat,
                         "directory":False},
                         "TextLoader":{"method":TextLoader,
                         "directory":False}}


splitting_method_mapping={"MarkdownHeaderTextSplitter":{"method":MarkdownHeaderTextSplitter,
                         "accepts documents":False},
                "RecursiveCharacterTextSplitter":{"method":RecursiveCharacterTextSplitter,
                         "accepts documents":True}}


def select_correct_parameters(constructor,**kwargs: Any):
     # Get the parameters of the loader
    parameters = inspect.signature(constructor).parameters
    if 'kwargs' in parameters:
        return kwargs
    else:
        return {key:kwargs[key] for key in parameters if key in kwargs.keys()}


def DocumentLoader(method:str,**kwargs: Any):

    loader=loading_method_mapping[method]["method"]

    return loader(**select_correct_parameters(loader,**kwargs))
    

class DocumentSplitter:
    def __init__(self, method:str,**kwargs: Any):
        self.method=method

        splitter=splitting_method_mapping[method]["method"]

        self.splitter=splitter(**select_correct_parameters(splitter,**kwargs))
    
    def split(self,doc):
        if type(doc)!="str" and splitting_method_mapping[self.method]["accepts documents"]:
            return self.splitter.split_documents(doc)
        elif type(doc)!="str" and not splitting_method_mapping[self.method]["accepts documents"]:
            docs=[]
            for d in doc:
                docs=docs+self.splitter.split_text(d.page_content)
            return docs
        elif type(doc)=="str":
            return self.splitter.split_text(doc)
        else:
            return []
        
def ExportDocs(docs:List[Document],export_path:str,export_name:str="export"):
    output_dir = os.path.abspath(export_path)
    os.makedirs(output_dir, exist_ok=True)
    for i,doc in enumerate(docs):
        with open(os.path.join(output_dir,f"{export_name}-{i}.json"), "w") as outfile:
            json.dump({"page_content":doc.page_content,"metadata":doc.metadata}, outfile)

def ReadDocs(path:str):
    docs=[]
    file_list=glob.glob(os.path.join(path,f"*.json"))
    file_list.sort(key=lambda x: int(x.split("-")[-1].replace(".json","")))
    for file_path in file_list:
        with open(file_path, 'r') as openfile:
            # Reading from json file
            doc = json.load(openfile)
        docs.append(Document(page_content=doc["page_content"],metadata=doc["metadata"]))
    return docs

def LoadAndSplit(method_loading:str,
                 method_splitting:str=None,
                 export_path:str=None,
                 export_name:str="export",
                 directory_loader_kwargs:dict=None,
                 splitter_kwargs:dict=None,
                 **kwargs: Any):
    
    if directory_loader_kwargs is None: directory_loader_kwargs=kwargs
    if splitter_kwargs is None: splitter_kwargs=kwargs
    if method_loading is not None: directory_loader_kwargs["loader_cls"]=loading_method_mapping[method_loading]["method"]

    directory_loader_kwargs=select_correct_parameters(DirectoryLoader,**directory_loader_kwargs)
    loader = DirectoryLoader(**directory_loader_kwargs)
    docs = loader.load()

    if method_splitting is not None:
        splitter = DocumentSplitter(method=method_splitting,**splitter_kwargs)
        docs=splitter.split(docs)

    if export_path is not None: ExportDocs(docs,export_path,export_name)

    return docs

embeddings_mapping={"AzureOpenAIEmbeddings":AzureOpenAIEmbeddings,
                    "HuggingFaceEmbeddings":HuggingFaceEmbeddings,
                    "GPT4AllEmbeddings":GPT4AllEmbeddings}

vector_store_mapping={
    "Chroma":{"store":Chroma,
              "save":False},
    "AzureSearch":{"store":AzureSearch,
                   "save":False},
    "ElasticsearchStore":{"store":ElasticsearchStore,
              "save":False},
    "FAISS":{"store":FAISS,
              "save":True}}

def EmbeddingsConstructor(embedding_map: str,**kwargs: Any):

    embeddings_model=embeddings_mapping[embedding_map]

    return embeddings_model(**select_correct_parameters(embeddings_model,**kwargs))

def VectorStoreConstructor(vector_store_map: str,**kwargs: Any):

    db=vector_store_mapping[vector_store_map]["store"]

    return db(**select_correct_parameters(db,**kwargs))


def IndexConstructor(embedding_map: str,
                     vector_store_map: str,
                     docs:Union[str, List[Document]],
                     db_kwargs:dict=None,
                     embedding_kwargs:dict=None,
                     export_path: str=None,
                     **kwargs: Any):

    if type(docs)==str: docs=ReadDocs(docs)

    if embedding_kwargs is None: embedding_kwargs=kwargs
    if db_kwargs is None: db_kwargs=kwargs
    
    embeddings=EmbeddingsConstructor(embedding_map,**embedding_kwargs)

    vector_store=vector_store_mapping[vector_store_map]["store"]

    db=vector_store.from_documents(documents=docs,
                                       embedding=embeddings,
                                       **select_correct_parameters(vector_store.from_documents,**db_kwargs))
    if export_path is not None and vector_store_mapping[vector_store_map]["save"]:
        db.save_local(export_path)

    return db
