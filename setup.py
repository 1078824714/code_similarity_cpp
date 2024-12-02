from setuptools import setup, find_packages
setup(
    name='code_similarity_cpp',
    version='0.1',
    packages=find_packages(),
    description='A Python library for calculating the similarity of cpp codes',
    url='https://github.com/yourusername/my_library',  
    install_requires=['tree_sitter_cpp','tree_sitter'],  
)