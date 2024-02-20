import abc
from pathlib import Path
import os
import json
from rag_blocks.base import ConfigMethodCaller



class Transform:
    @abc.abstractmethod
    def transform(self, docs):
        pass

class ExportDocsTransform(Transform):
    def __init__(self, export_path):
        self.export_path = Path(export_path)

    def transform(self, docs):
        directory = self.export_path.parent
        os.makedirs(directory, exist_ok=True)
        for i,doc in enumerate(docs):
            with open(self.export_path, "w") as outfile:
                json.dump({"page_content":doc.page_content,"metadata":doc.metadata}, outfile)
        return docs

class TransformChooserFromConfig(Transform):
    def __init__(self, config):
        if isinstance(config, list):
            self.transformer = ChainTransforms(config)
        else:
            self.transformer = TransformWrapperFromConfig(config)
    
    def transform(self, docs):
        return self.transformer.transform(docs)
    

class TransformWrapperFromConfig(Transform, ConfigMethodCaller):
    def __init__(self, config):
            ConfigMethodCaller.__init__(self, config, default_name="transform", default_behavior=lambda docs: docs)
    
    def transform(self, docs):
            return self.method(docs)

class ChainTransforms(Transform):
    def __init__(self, transforms_config):
        self.transforms = [TransformWrapperFromConfig(config) for config in transforms_config]
    
    def transform(self, docs):
        for transformer in self.transforms:
            docs = transformer.transform(docs)
        return docs
