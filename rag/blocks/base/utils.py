import os
from importlib import import_module

def dynamic_import(class_path):
    module_name, class_name = class_path.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, class_name)

def is_global(value):
    return value.startswith("$global:")

def is_import(value):
    return value.startswith("$import:")

def is_env(value):
    return value.startswith("$env:")

def handle_global(value):
    global_key = value[8:]  # Remove the prefix
    return globals().get(global_key)

def handle_env(value):
    env_key = value[5:]  # Remove the prefix
    return os.getenv(env_key)

def handle_import(value):
    import_key = value[8:]
    return dynamic_import(import_key)

def handle_special(name):
    if is_env(name):
        return handle_env(name)
        # Fetch the value from environment variables
    elif is_global(name):
        return handle_global(name)
        # Fetch the value from globals
    elif is_import(name):
        return handle_import(name)
    else:
        return name

def process_args(args):
    special_class_key =  "class_name"
    special_init_key =  "init_args"
    processed_args = {}

    def process_value(value):
        if isinstance(value, str):
            return handle_special(value)
        elif isinstance(value, dict):
            if special_class_key in value and is_import(value[special_class_key]):
                class_obj = handle_import(value[special_class_key])
                init_args = process_args(value.get(special_init_key, {}))
                return class_obj(**init_args)
            # Recursively process the nested dictionary
            return {k: process_value(v) for k, v in value.items()}
        else:
            return value

    for key, value in args.items():
        processed_args[key] = process_value(value)
    
    print(processed_args)

    return processed_args