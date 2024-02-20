from setuptools import setup, find_packages

setup(
    name='rag',
    version='0.1',
    packages=find_packages(),  # This should automatically find 'rag.blocks' and 'rag.utils'
)

#setup(
#    name='rag',
#    version='0.1',
#    packages=find_packages(),
    # Include any additional package directories here
#    package_dir={'rag_blocks': 'rag/blocks', 'rag_utils': 'rag/utils'},
    # Specify any package data, scripts, and dependencies here
#)
