from .utils import process_args, handle_import
from collections.abc import Iterable
import functools

class NoArgument:
    pass

NO_ARGUMENT = NoArgument()

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

def unwrap_wrap(func, arg_wrapper):
    if not isinstance(arg_wrapper, ArgumentsWrapper):
        raise ValueError("Argument must be an instance of ArgumentsWrapper")
    args, kwargs = arg_wrapper.unwrap()
    result = func(*args, **kwargs)
    # If the result is already an ArgumentsWrapper, return it directly.
    if isinstance(result, ArgumentsWrapper):
        return result
    # Automatically wrap based on the output type.
    if isinstance(result, tuple):
        return ArgumentsWrapper(args=result, single_arg=False)
    else:
        return ArgumentsWrapper(args=result, single_arg=True)
 
class ConfigMethodCaller:
    def __init__(self, config, default_name=None, default_behavior=lambda **kwargs: kwargs):
        class_obj = handle_import(config['class_name'])
        init_args = process_args(config.get('init_args', {}))
        
        # Attempt to create an instance of the class
        try:
            class_instance = class_obj(**init_args)
            print(f"CREATED CLASS {class_obj}({init_args})")
            target = class_instance
        except TypeError as e:
            print(e)
            # If the class cannot be instantiated, use the class itself as the target for method resolution
            class_instance = None
            target = class_obj


        method_name = config.get('method', {}).get('name', default_name)
        method = getattr(target, method_name, None)

        if not method:
            print(f"Couldn't find {method_name} in {target}")
            self.method = default_behavior
        else:
            # Process method arguments if any
            method_kwargs = process_args(config.get('method', {}).get("args", {}))

            def wrapped_method(argument=NO_ARGUMENT):
                if isinstance(argument, ArgumentsWrapper):
                    argument.kwargs.update(method_kwargs)
                else:
                    argument=ArgumentsWrapper(args=argument, kwargs=method_kwargs, single_arg=True)
                print(f"Calling {method} with {argument.args} and {argument.kwargs}")
                return unwrap_wrap(method, argument)
                
            self.method = wrapped_method                

__all__ = [ConfigMethodCaller, ArgumentsWrapper]