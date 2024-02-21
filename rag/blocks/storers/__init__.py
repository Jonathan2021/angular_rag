import abc
from rag.blocks.base import ConfigMethodCaller

class Storer(abc.ABC):
    def store(self, *args, **kwargs):
        return self._store(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        return self.store(*args, **kwargs)

    abc.abstractmethod
    def _store(self, *args, **kwargs):
        pass

class StorerFromConfig(Storer, ConfigMethodCaller):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="store", default_behavior=lambda docs: None)
    
    def _store(self, *args, **kwargs):
        return self.method(*args, **kwargs)

__all__ = [StorerFromConfig]