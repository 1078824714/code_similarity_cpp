# What is it
-**code_similarity_cpp** is a Python package that Calculate the similarity between two cpp codes or the maximum similarity between the first cpp code and a list of cpp codes.
-It uses the AST (Abstract Syntax Tree) of the C++ code with the winnowing algorithm and jaccard similarity to calculate the similarity.
# Where to get it
```sh
#PyPI
pip install code_similarity_cpp
```
# Example
```python
import code_similarity_cpp

code1 = r"""
your code here
"""
code2 = r"""
your code here
"""
path1="your path to code1"
path2="your path to code2"

#Calculate the similarity between two cpp codes
similarity0 = code_similarity_cpp.Similarity(code1=code1, code2=code2)
similarity1 = code_similarity_cpp.Similarity(path1=path1, path2=path2)
similarity2 = code_similarity_cpp.Similarity(code1=code1, path2=path2)
similarity3 = code_similarity_cpp.Similarity(path1=path1, code2=code2)
```
```python
import code_similarity_cpp

code1 = r"""
your code here
"""
code2 = [r"""your code here""", r"""your code here""", r"""your code here""",...]]
path1="your path to code1"
path2=["your path to code2", "your path to code3", "your path to code4", ...]

#Calculate the maximum similarity between the first cpp code and a list of cpp codes
similarity0 = code_similarity_cpp.MaxSimilarity(code1=code1, code2=code2)
similarity1 = code_similarity_cpp.MaxSimilarity(path1=path1, path2=path2)
similarity2 = code_similarity_cpp.MaxSimilarity(code1=code1, path2=path2)
similarity3 = code_similarity_cpp.MaxSimilarity(path1=path1, code2=code2)
```