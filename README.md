# Modular Retrieaval Augmented Generation Web app
The focus here is on the backend and the storing of documents in a vector database. A generic front-end is available for test purpose.

## Usage flow

- **Vector Store creation**
You typically want to create a vector store containing chunks of your documents, later used for querying.
This is usually a one-off operation, or with very few updates.

- **Querying your knowledge base**
This is done via the web app. The server queries the vector store for document chunks matching the query and returns an answer based on a mix of those documents and your original question.
Unlike creating the vector store, this can have quite the usage volume.

## Get up and running

- **Clone this repo**: `git clone git@github.com:Jonathan2021/angular_rag.git`
- **Launch the server**: Go into the root directory of this repo and run `make up` (To modify the usage, you can modify the environment variables containing the paths to the config files. Open the Makefile to understand more)
- **Get the front end and enjoy**: By going to http://localhost:4200/ (or whatever you have modified this to be)

## Quick Code overview
The objective was to decouple each step and make them configurable as much as possible. To do so, we use yaml config files with some special structure and syntax keywords to specify behavior (keyword syntax is $special_thing:).

### Yaml Config files

**Example configuration files are in rag/configurations**

#### Special Syntax
- **$import:** : The class specified after this flag will be instantiated.
- **$env:** : The name specified after this flag will be fetched from the environment.
- **$global:** : **WARNING, USE THE OTHER 2**, the specified name is fetched from globals.

#### Special structure
The yaml files are parsed internally to create pipelines. They specify the behavior of each element of the pipeline + some other behavior of the script.

Pipelines often call methods from various classes sequentially. Each element in a pipeline is situated at the root of the yaml file. Following is a snippet of a possible yaml configuration file.

```
env_path: /path/to/env/file

something: something_value

pipeline_element_1:
  class_name: "$import:module.some_class"
  init_args:
    arg1: "value1"
    arg2:
      class_name: "$import:module.some_other_class"
      init_args:
        arg21: "value"
        arg22: "$env:some_env_var"
  method:
    name: "some_class_method_name"
    args:
      arg1: "$env:something"
      arg2: "$import:module.a_class_somewhere"

pipeline_element_2:
  class_name: "$import:module.some_class_2"
  method:
    name: "some_class_2_method_name"
    args:
      arg1: "$env:something2"
      arg2: some_int_value

pipeline_elemnt_3:
  class_name: "$import:module.class3"
  init_args:
    arg1: some_float
```

Depending on the script you call, it will probably expect you to have a bunch of variables such as `env_path` or `something` to tweak behavior, and the names of some elements of the pipeline it is expected to create.
As you can see here, pipeline elements at root level are usually classes instantiated or not, with a method to call at runtime.
Argument initialization is done recursively and is parsed using the special syntax we explained before.

For `pipeline_element_2`, th user may have intended 2 things since `init_args` isn't present. Both options are tried in order:
  - it will try to create an object of the class with no arguments and it will call the given method on this instance
  - the instance creation fails and it tries to call the method as a static method of the class.

For `pipeline_element_3`, no `method` is given. For most pipelines, a default is given internally. But it is **best practice to explicit it nonetheless**.
If the wanted behavior was for the method to return the object itself, then it should be wrapped in `rag.blocks.base.ReturnSelfWrapper` with the `get` method.

### Inner workings of the code.
Will do later.
