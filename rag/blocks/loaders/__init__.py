import abc
from rag.blocks.base import ConfigMethodCaller
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader


class Loader:
    def load(self, *args, **kwargs):
        return self._load(*args, **kwargs)
    
    @abc.abstractmethod
    def _load(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.load(*args, **kwargs)

class AzureDocLoader(Loader, AzureAIDocumentIntelligenceLoader):
    def __init__(self, file_path, **kwargs):
        AzureAIDocumentIntelligenceLoader.__init__(self, file_path=file_path, **kwargs)
    
    def _load(self):
        return AzureAIDocumentIntelligenceLoader.load(self)

class LoaderFromConfig(ConfigMethodCaller, Loader):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="load", default_behavior=lambda : None)
    
    def _load(self, *args, **kwargs):
        return self.method(*args, **kwargs)

__all__ = [LoaderFromConfig, AzureDocLoader]