import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser
import re
import hashlib
import subprocess
import tempfile
import os
import math

class Similarity:

    def __init__(self,code1:str=None,code2:str|list=None,path1:str=None,path2:str|list=None,k=3,t=5,decode='utf-8',processby='g++'):
        """
        Calculate the similarity between two cpp codes or the maximum similarity between the first cpp code and a list of cpp codes.

        code1:the first cpp code

        code2:the second cpp code or a list of cpp codes

        path1:the path of the first cpp code

        path2:the path of the second cpp code or a list of cpp codes

        k:k-gram size for winnowing

        t:window size for winnowing

        decode: utf-8 gbk...

        processby: g++ clang++...
        """
        self.__k=k                    # k-gram size for winnowing
        self.__t=t                    # window size forwinnowing
        self.__decode=decode          # decode: utf-8 gbk...
        self.__processby=processby    # processor: g++ clang++...
        self.__parser=Parser()
        self.__parser.language=Language(tscpp.language())
        try:
            match (code1,path1):
                case (None,None):raise ValueError("code1 or path1 should not be None")
                case (_,_):raise ValueError("code1 and path1 should not be both not None")
                case (code,None):self.__code1=code
                case (None,path):
                    match path:
                        case str():self.__code1=self.__readfile(path)
                        case _:raise ValueError("path1 should be str")
            match (code2,path2):
                case (None,None):raise ValueError("code2 or path2 should not be None")
                case (_,_):raise ValueError("code2 and path2 should not be both not None")
                case (code,None):self.__code2=code
                case (None,path):
                    match path:
                        case str():self.__code2=self.__readfile(path)
                        case list():self.__code2=self.__readfile_mul(path)
                        case _:raise ValueError("path2 should be str or list")
        except ValueError as e:
            print(e)
            return None
        
    def __readfile(self,file_path):
        with open(file_path, 'r', encoding=self.__decode) as file:
            code = file.read()
        return code

    def __readfile_mul(self,file_path_list):
        code_list=[]
        for file_path in file_path_list:
            code=self.__readfile(file_path)
            code_list.append(code)
        return code_list

    def __preprocess(self):

        def preprocessor1(code):
            i=code.find('#include')
            while(i!=-1):
                j=code.find('\n',i+7)+1
                code=code[:i]+code[j:]
                i=code.find('#include')          
            return code
        
        def preprocess_cpp_code(code,decode):
            with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as temp_file:
                temp_file.write(code.encode(decode))
                temp_file_path = temp_file.name

            try:
                result = subprocess.run([self.__processby, '-E', temp_file_path], capture_output=True, text=True, check=True)
                preprocessed_code = result.stdout
                return preprocessed_code

            except subprocess.CalledProcessError as e:
                print(f"process error: {e.stderr}")
                return None

            finally:
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    print(f"delete temp file error: {e}")

        def preprocessor2(code):

            def macro(s,code):      ##
                e=code.find('\n',s+2)+1
                code_new=code[:s]+code[e:]
                return code_new
            
            def namespace(code):       #namespace
                code_new=re.sub('using\s+namespace\s+std;','',code)
                code_new=re.sub('std\s+::','',code_new)
                code_new=re.sub('std::','',code_new)
                return code_new
            
            def brackets(code):        #()[]<>{}
                code_new=re.sub('\(\)','',code)
                code_new=re.sub('\[\]','',code_new)
                code_new=re.sub('\<\>','',code_new)
                code_new=re.sub('\{\}','',code_new)
                return code_new
            
            i=code.find('#')
            while(i!=-1):
                code=macro(i,code)
                i=code.find('#')
            
            code=namespace(code)
            code=brackets(code)
         
            return code

        self.__code1=preprocessor1(self.__code1)
        self.__code1=preprocess_cpp_code(self.__code1,self.__decode)
        self.__code1=preprocessor2(self.__code1)
        self.__code2=preprocessor1(self.__code2)
        self.__code2=preprocess_cpp_code(self.__code2,self.__decode)
        self.__code2=preprocessor2(self.__code2)

    def __ast(self,code):
        tree=self.__parser.parse(bytes(code, 'utf8'))
        root_node=tree.root_node
        ast_list=[]         # ast_list: node type list of ast
        def ast_dfs(node):
            # DFS
            nonlocal  ast_list
            # from cst to ast
            def traverse(node):
                children=node.children
                for child in node.children:
                    if(child.type in ['{','}','[',']','(',')',';','\'','\"',',']):
                        children.remove(child)
                if(len(children)==1):           #only one child
                    node=children[0]
                    traverse(node)     
                return node
            node=traverse(node)
            node_type = node.type
            ast_list.append(node_type)
            # traverse children
            for child in node.children:
                ast_dfs(child)
        ast_dfs(root_node)       
        return ast_list

    def __winnowing(self,text):

        def hash_function(text):                                    #hash function
            return int(hashlib.sha1(text.encode()).hexdigest(), 16)
        
        n = len(text)
        hashes = [] 
        # calculate k-gram hash values
        for i in range(n - self.__k + 1):
            k_gram = text[i:i + self.__k]
            k_gram=''.join(k_gram)
            h = hash_function(k_gram)
            hashes.append(h)

        # calculate fingerprints by sliding window
        window = []
        for i in range(self.__t):
            window.append(hashes[i])
        fingerprints = []
        fingerprints.append(min(window))
        for i in range(len(hashes)-self.__t):
            window.remove(window[0])
            window.append(hashes[i+self.__t])
            min_hash = min(window)
            if min_hash==window[self.__t-1]:
                fingerprints.append(min_hash)

        return set(fingerprints)

    def __similarity(self,ast1,ast2):
        self.__preprocess()

        def jaccard_index(setA, setB):                  #jaccard
            intersection = setA.intersection(setB)
            union = setA.union(setB)
            return len(intersection) / len(union) if len(union) > 0 else 0
        
        def relu(x):            # discretize the data
            if x<0.5:
                return x**2
            elif x<0.8:
                return x
            else:
                return math.sqrt(x)

        # calculate fingerprints
        fingerprints1 = self.__winnowing(ast1)
        fingerprints2 = self.__winnowing(ast2)

        # calculate similarity
        similarity = relu(jaccard_index(fingerprints1, fingerprints2))
        return similarity
    
    def similarity(self):
        if(type(self.__code2)==list):
            max_similarity=0
            ast1=self.__ast(self.__code1)
            for code in self.__code2:
                ast2=self.__ast(code)
                max_similarity=max(max_similarity,self.__similarity(ast1,ast2))
            return max_similarity
        else:
            ast1=self.__ast(self.__code1)
            ast2=self.__ast(self.__code2)
            return self.__similarity(ast1,ast2)
