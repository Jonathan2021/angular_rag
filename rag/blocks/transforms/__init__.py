import abc
from pathlib import Path
import os
import json
from collections.abc import Iterable
from rag.blocks.base import ConfigMethodCaller, ArgumentsWrapper

class Transform(abc.ABC):
    def transform(self, docs):
        return self._transform(docs)

    @abc.abstractmethod
    def _transform(self, docs):
        pass

class ExportDocs(Transform):
    def __init__(self, export_path):
        self.export_path = Path(export_path)

    def _transform(self, docs):
        directory = self.export_path.parent
        os.makedirs(directory, exist_ok=True)
        for i,doc in enumerate(docs):
            print(doc)
            with open(self.export_path, "w") as outfile:
                json.dump({"page_content":doc.page_content,"metadata":doc.metadata}, outfile)
        return docs

class TransformChooserFromConfig(Transform):
    def __init__(self, config):
        if isinstance(config, list):
            self.transformer = ChainTransforms(config)
        else:
            self.transformer = TransformWrapperFromConfig(config)
    
    def _transform(self, docs):
        return self.transformer.transform(docs)

class UnzipDocuments(Transform):
    def _transform(self, docs):
        content = []
        metadata = []
        for doc in docs:
            content.append(doc.page_content)
            metadata.append(doc.metadata)
        return content, metadata

    
class ArgumentAdapter(Transform):
    def __init__(self, key_mapping = None, key_transpose = None):
        if key_transpose:
            assert isinstance(key_transpose, dict), "key_transpose needs to be a dict"
            self.key_transpose = key_transpose
        else:
            self.key_transpose = {}

        if key_mapping is not None:
            self.key_mapping = key_mapping if isinstance(key_mapping, Iterable) else [key_mapping]
        else:
            self.key_mapping = []
    
    def _dict_transpose(self, entry):
        assert (isinstance(entry, dict)), "Needs to be a dictionary"
        new_entry = {}
        for key, value in entry.items():
            new_entry[self.key_transpose.get(key, key)] = value
        return new_entry
    
    def _key_mapping(self, entry):
        if not isinstance(entry, Iterable):
            entry = [entry]

        assert(len(self.key_mapping) == len(entry)), "Not the same number of keys and values"
        return ArgumentsWrapper(kwargs=dict(zip(self.key_mapping, entry)))
    
    def transform(self, *args, **kwargs):
        return self._transform(*args, **kwargs)
    
    def _transform(self, *args, **kwargs):
        new_kwargs = None
        new_kwargs = self._key_mapping(args)
        new_kwargs.kwargs.update(self._dict_transpose(kwargs))
        return new_kwargs

class UnwrapArguments(Transform):
    def _transform(self, wrapped):
        if isinstance(wrapped, ArgumentsWrapper):
            return wrapped.args, wrapped.kwargs
        return wrapped

    

class TransformWrapperFromConfig(Transform, ConfigMethodCaller):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="transform", default_behavior=lambda docs: docs)
    
    def _transform(self, docs):
        return self.method(docs)

class ChainTransforms(Transform):
    def __init__(self, transforms_config):
        self.transforms = [TransformWrapperFromConfig(config) for config in transforms_config]
    
    def _transform(self, docs):
        for transformer in self.transforms:
            docs = transformer.transform(docs)
        return docs

__all__ = [ChainTransforms, TransformWrapperFromConfig, ArgumentAdapter, TransformChooserFromConfig, UnzipDocuments, ExportDocs]