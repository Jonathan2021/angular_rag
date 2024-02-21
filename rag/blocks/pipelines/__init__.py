import abc
from collections.abc import Iterable
from rag.blocks.loaders import LoaderFromConfig
from rag.blocks.transforms import TransformFromConfig
from rag.blocks.storers import StorerFromConfig
from rag.blocks.base import NO_ARGUMENT, NO_OUTPUT, WrappedOutput


class ArgumentsWrapper:
    def __init__(self, args=NO_ARGUMENT, kwargs=NO_ARGUMENT, single_arg=True):
        if kwargs is not NO_ARGUMENT:
            if isinstance(kwargs, ArgumentsWrapper):
                self.kwargs = kwargs.kwargs
            elif isinstance(kwargs, dict):
                self.kwargs = kwargs
            else:
                raise "Kwargs passed to ArgumentsWrapper has to be a dict or an ArgumentsWrapper"        
        else:
            self.kwargs = {}

        if args is not NO_ARGUMENT:
            if isinstance(args, ArgumentsWrapper):
                self.args = args.args
                self.kwargs.update(args.kwargs)
            elif isinstance(args, Iterable) and not single_arg:
                self.args = args
            else:
                self.args = [args]
                self.single_arg = True
        else:
            self.args = []

    def unwrap(self):
        return self.args, self.kwargs
    
    @classmethod
    def from_output(cls, output):
        # If the result is already an ArgumentsWrapper, return it directly.
        wrapped = None
        if isinstance(output, ArgumentsWrapper):
            wrapped = output
        # Automatically wrap based on the output type.
        elif output is NO_OUTPUT:
            wrapped = cls(args=NO_ARGUMENT)
        elif isinstance(output, WrappedOutput):
            output = output.get()
            if isinstance(output, dict):
                wrapped = cls(kwargs=output)
            elif isinstance(output, tuple):
                wrapped = cls(args=output, single_arg=False)
            else:
                wrapped = cls(args=output, single_arg=True)
        else:
            wrapped = cls(args=output, single_arg=True)
        return wrapped


def unwrap_wrap(func, arg_wrapper):
    if not isinstance(arg_wrapper, ArgumentsWrapper):
        raise ValueError("Argument must be an instance of ArgumentsWrapper")
    args, kwargs = arg_wrapper.unwrap()
    result = func(*args, **kwargs)
    return ArgumentsWrapper.from_output(result)

class PassThroughStep:
    def __call__(self, arg):
        return arg

PASS_THROUGH = PassThroughStep()

class Pipeline(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *steps):
        self.steps = steps
    
    def process(self, *args, **kwargs):
        single_arg = len(args) == 1
        if not len(args):
            args = NO_ARGUMENT
        arg = ArgumentsWrapper(args, kwargs, single_arg)
        
        for step in self.steps:
            arg = unwrap_wrap(step, arg)
        return arg.unwrap
        

class VectorStoringPipeline(Pipeline):
    def __init__(self, load, transforms, store):
        Pipeline.__init__(self, load, *transforms, store)


class VectorPipelineFromConfig(VectorStoringPipeline):
    def __init__(self, config):
        assert ("loader" in config), "Config needs to have a loader"
        load = LoaderFromConfig(config["loader"]).load
        print("Initiated loader")
        
        if "transform" in config:
            if isinstance(config["transform"], Iterable):
              transforms = [TransformFromConfig(conf).transform for conf in config["transform"]]
            else:
                transforms = [TransformFromConfig(config["transform"]).transform]
            print("Initiated transform")
        else:
            transforms = [PASS_THROUGH]
        
        if "store" in config:
            store = StorerFromConfig(config["store"]).store
            print("Initiated Store")
        else:
            store = PASS_THROUGH

        VectorStoringPipeline.__init__(self, load, transforms, store)

__all__ = [VectorStoringPipeline, VectorPipelineFromConfig, ArgumentsWrapper]