import abc
from pathlib import Path
import os
import json
from collections.abc import Iterable
from rag.blocks.base import ConfigMethodCaller
from rag.blocks.base import WrappedOutput

class Transform(abc.ABC):
    def transform(self, *args, **kwargs):
        return self._transform(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        return self.transform(*args, **kwargs)

    @abc.abstractmethod
    def _transform(self, *args, **kwargs):
        pass


class ExportDocs(Transform):
    def __init__(self, export_path, json_lines=True):
        self.export_path = Path(export_path)
        
        def _lines_writer(file, docs):
            for doc in docs:
                file.write(
                    json.dumps({"page_content":doc.page_content,"metadata":doc.metadata}) + "\n"
                )
        
        def _json_writer(file, docs):
            docs_list = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
            data_to_write = {"docs": docs_list}
            json.dump(data_to_write, file)
        
        self.writer = _lines_writer if json_lines else _json_writer

    def _transform(self, docs):
        directory = self.export_path.parent
        os.makedirs(directory, exist_ok=True)
        
        with open(self.export_path, "w") as outfile:
            self.writer(outfile, docs)
        return docs


class UnzipDocuments(Transform):
    def _transform(self, docs):
        content = []
        metadata = []
        for doc in docs:
            content.append(doc.page_content)
            metadata.append(doc.metadata)
        return content, metadata

    
class ArgumentAdapter(Transform):
    def __init__(self, key_mapping, wrap_output=True):
        mechanism = lambda x: x
        if isinstance(key_mapping, dict):
            def dict_transpose(entry):
                new_entry = {}
                for key, value in entry.items():
                    new_entry[key_mapping.get(key, key)] = value
                return new_entry
            mechanism = dict_transpose
        else:
            def list_transpose(entry):
                if not isinstance(entry, Iterable):
                    entry = [entry]
                assert(len(key_mapping) == len(entry)), "Not the same number of keys and values"
                return dict(zip(key_mapping, entry))
            mechanism = list_transpose
        self.mechanism = mechanism
        self.wrap_output = OutputWrapper().transform if wrap_output else lambda x: x
    
    def _transform(self, entry):
        return self.wrap_output(self.mechanism(entry)) 

class OutputWrapper(Transform):
    def _transform(self, output):
        return WrappedOutput(output)

class OutputUnwrapper(Transform):
    def _transform(self, wrapped):
        assert isinstance(wrapped, WrappedOutput), "OutputUnwrapper expects a WrappedOutput Argument"
        return wrapped.get()

class TransformFromConfig(Transform, ConfigMethodCaller):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="transform", default_behavior=lambda docs: docs)
    
    def _transform(self, *args, **kwargs):
        return self.method(*args, **kwargs)

__all__ = [TransformFromConfig, ArgumentAdapter, UnzipDocuments, ExportDocs, Transform]