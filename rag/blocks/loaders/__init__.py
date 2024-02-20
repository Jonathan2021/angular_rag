import abc
from rag_blocks.base import ConfigMethodCaller
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader


class Loader:
    @abc.abstractmethod
    def load(self):
        pass

class AzureDocLoader(AzureAIDocumentIntelligenceLoader, Loader):
    def __init__(self, file_path, **kwargs):
        AzureAIDocumentIntelligenceLoader.__init__(self, file_path=file_path, **kwargs)
    
    def load(self):
        AzureAIDocumentIntelligenceLoader.load(self)

class LoaderFromConfig(ConfigMethodCaller, Loader):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="load", default_behavior=lambda : None)
    
    def load(self):
        return self.method()

__all__ = [LoaderFromConfig, AzureDocLoader]