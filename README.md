# What is it
**code_similarity_cpp** is a Python package that Calculate the similarity between two cpp codes or the maximum similarity between the first cpp code and a list of cpp codes.

It uses the AST (Abstract Syntax Tree) of the C++ code with the winnowing algorithm and jaccard similarity to calculate the similarity.
# Where to get it
```sh
#PyPI
pip install git+https://github.com/1078824714/code_similarity_cpp
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
model = code_similarity_cpp.Similarity()
similarity0,_ = model.similarity(code1=code1, code2=code2)
similarity1,_ = model.similarity(path1=path1, path2=path2)
similarity2,_ = model.similarity(code1=code1, path2=path2)
similarity3,_ = model.similarity(path1=path1, code2=code2)
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
#mostsimilarcode from code2
model = code_similarity_cpp.Similarity()
similarity0,mostsimilarcode0 = model.similarity(code1=code1, code2=code2)
similarity1,mostsimilarcode1 = model.similarity(path1=path1, path2=path2)
similarity2,mostsimilarcode2 = model.similarity(code1=code1, path2=path2)
similarity3,mostsimilarcode3 = model.similarity(path1=path1, code2=code2)
```
```python
import code_similarity_cpp

path="your path to code"

#dot:Digraph object,from graphviz library
dot=model.Print_tree(path=path)

#example
dot.render('code.gv',view=True)
```
```python
import code_similarity_cpp

path1="your path to code1"
path2=["your path to code2", "your path to code3", "your path to code4", ...]

model = code_similarity_cpp.Similarity()
_,mostsimilarcode = model.similarity(path1=path1, path2=path2)

# Return the duplication code between the first cpp code and the second cpp code.
duplication_str1,duplication_str2 = model.Duplication(path1=path1, code2=mostsimilarcode)
```
