from functools import partial
from .utils import process_args, handle_import


class ConfigMethodCaller:
    def __init__(self, config, default_name=None, default_behavior=lambda **kwargs: kwargs):
        class_obj = handle_import(config['class_name'])
        init_args = process_args(config.get('init_args', {}))
        
        # Attempt to create an instance of the class
        try:
            class_instance = class_obj(**init_args)
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
            method_args = process_args(config.get('method', {}).get("args", {}))
            self.method = partial(method, **method_args)

__all__ = [ConfigMethodCaller]