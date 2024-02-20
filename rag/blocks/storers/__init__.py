import abc
from rag_blocks.base import ConfigMethodCaller

class Storer:
    abc.abstractmethod
    def store(self, docs):
        pass

class StorerFromConfig(ConfigMethodCaller, Storer):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="store", default_behavior=lambda docs: None)
    
    def store(self, docs):
        return self.method(docs)

__all__ = [StorerFromConfig]