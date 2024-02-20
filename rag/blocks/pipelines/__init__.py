import abc
from rag.blocks.loaders import LoaderFromConfig
from rag.blocks.transforms import TransformChooserFromConfig
from rag.blocks.storers import StorerFromConfig


class Pipeline:
    @abc.abstractmethod
    def process(self):
        pass

class VectorStoringPipeline(Pipeline):
    def __init__(self, loader, transformer, storer):
        self.loader = loader
        self.transformer = transformer
        self.storer = storer

    def process(self):
        docs = self.loader.load()
        print("Loaded docs")
        print(docs)
        docs = self.transformer.transform(docs)
        print("Transformed docs")
        print(docs)
        res = self.storer.store(docs)
        print(self.storer.method)
        print("Stored docs")
        return res


forward = lambda x: x

class VectorPipelineFromConfig(VectorStoringPipeline):
    def __init__(self, config):
        assert ("loader" in config), "Config needs to have a loader"
        loader = LoaderFromConfig(config["loader"])
        print("Initiated loader")
        
        if "transform" in config:
            transformer = TransformChooserFromConfig(config["transform"])
            print("Initiated transform")
        else:
            transformer = forward
        
        if "store" in config:
            storer = StorerFromConfig(config["store"])
            print("Initiated Store")
        else:
            storer = forward

        VectorStoringPipeline.__init__(self, loader, transformer, storer)

__all__ = [VectorStoringPipeline, VectorPipelineFromConfig]