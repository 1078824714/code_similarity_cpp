from setuptools import setup

setup(
    name='code_similarity_cpp',
    version='0.2',
    py_modules=['code_similarity_cpp'],
    description='A Python library for calculating the similarity of cpp codes',
    author='1078824714',
    author_email='1078824714@qq.com',
    url='https://github.com/1078824714/code_similarity_cpp',  
    install_requires=[
        'tree_sitter_cpp', 
        'tree_sitter', 
        'graphviz'
    ],  
)
