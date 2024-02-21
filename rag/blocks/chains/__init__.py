import abc
from rag.blocks.base import ConfigMethodCaller



class Chainer(abc.ABC):
    def chain(self, *args, **kwargs):
        return self._chain(*args, **kwargs)
    
    @abc.abstractmethod
    def _chain(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.chain(*args, **kwargs)

class ChainerFromConfig(Chainer, ConfigMethodCaller):
    def __init__(self, config):
        ConfigMethodCaller.__init__(self, config, default_name="chain", default_behavior=lambda : None)
    
    def _chain(self, *args, **kwargs):
        return self.method(*args, **kwargs)

__all__ = [ChainerFromConfig]