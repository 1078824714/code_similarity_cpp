import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser
from graphviz import Digraph
import re
import hashlib
import subprocess
import tempfile
import os
import math

class Similarity:
    def __init__(self,k=3,t=5,decode='utf-8',processby='g++'):
        """
        Calculate the similarity between two cpp codes or the maximum similarity between the first cpp code and a list of cpp codes.

        k:k-gram size for winnowing

        t:window size for winnowing

        decode: utf-8 gbk...

        processby: g++ clang++...
        """
        self.__code1=''
        self.__code2=''
        self.__k=k                    # k-gram size for winnowing
        self.__t=t                    # window size forwinnowing
        self.__decode=decode          # decode: utf-8 gbk...
        self.__processby=processby    # processor: g++ clang++...
        self.__parser=Parser()
        self.__parser.language=Language(tscpp.language())

    def similarity(self,code1:str=None,code2:str|list=None,path1:str=None,path2:str|list=None):
        """
        Return the similarity and the most similar code.

        code1:the first cpp code

        code2:the second cpp code or a list of cpp codes

        path1:the path of the first cpp code

        path2:the path of the second cpp code or a list of cpp codes
        """
        self.__code1=''
        self.__code2=''
        try:
            self.__readfile_str1(code1,path1)
            self.__readfile_list(code2,path2)
        except ValueError as e:
            print(e)
            return None
        
        self.__code1=self.__preprocess_after(self.__code1)
        match self.__code2:
            case str():
                code2=self.__code2
                self.__code2=self.__preprocess_after(self.__code2)
                ast1=self.__ast_after(self.__code1)
                ast2=self.__ast_after(self.__code2)
                return self.__similarity(ast1,ast2),code2
            case list():
                simliar_code=''
                max_similarity=0
                ast1=self.__ast_after(self.__code1)
                for code in self.__code2:
                    code_temp=code
                    code=self.__preprocess_after(code)
                    ast2=self.__ast_after(code)
                    temp=max(max_similarity,self.__similarity(ast1,ast2))
                    if temp!=max_similarity:
                        max_similarity=temp
                        simliar_code=code_temp
                return max_similarity,simliar_code

    def Print_tree(self,code:str=None,path:str=None):
        ''' 
        return dot: Digraph object,from graphviz library

        code:the cpp code to be drawn

        path:the path of the cpp code to be drawn
        '''
        self.__code1=''
        try:
            self.__readfile_str1(code,path)
        except ValueError as e:
            print(e)
            return None
        node_list,edge_list,_=self.__cst_before(self.__code1)
        return self.__draw_tree(node_list,edge_list)

    def Duplication(self,code1:str=None,code2:str=None,path1:str=None,path2:str=None):
        """
        Return the duplication code between the first cpp code and the second cpp code.

        code1:the first cpp code

        code2:the second cpp code

        path1:the path of the first cpp code

        path2:the path of the second cpp code    
        """
        def long_enough(sum):
            nonlocal codewithtype1,codewithtype2
            length=min(len(codewithtype1),len(codewithtype2))
            if sum<30:
                return False
            if sum<length/5:
                return False
            return True
        
        self.__code1=''
        self.__code2=''
        try:
            self.__readfile_str1(code1,path1)
            self.__readfile_str2(code2,path2) 
        except ValueError as e:
            print(e)
            return None
        self.__preprocess_before()
        _,_,codewithtype1=self.__cst_before(self.__code1)
        _,_,codewithtype2=self.__cst_before(self.__code2)

        duplication_list1=[]
        duplication_list2=[]
        number=1
        i=0
        pos=0
        while i < len(codewithtype1):
            sum=0
            list1=[]
            list2=[]
            temp_list1=[]
            temp_list2=[]
            for j in range(pos,len(codewithtype2)):
                if(i+sum>=len(codewithtype1)):
                    pos=len(codewithtype2)
                    break
                if codewithtype1[i+sum][0]==codewithtype2[j][0]:
                    temp_list1.append(codewithtype1[i+sum][1])
                    temp_list2.append(codewithtype2[j][1])
                    if codewithtype1[i+sum][1] in ['}',')',';']:
                        list1.append(' '.join(temp_list1))
                        list2.append(' '.join(temp_list2))
                        temp_list1=[]
                        temp_list2=[]
                    sum+=1
                    if j==len(codewithtype2)-1:
                        pos=len(codewithtype2)
                        break
                    continue
                if sum>0:
                    pos=j
                    break
                if j==len(codewithtype2)-1:
                    pos=len(codewithtype2)
                    break
            if long_enough(sum):
                duplication_list1.append(str(number)+':')
                duplication_list1.append(' '.join(list1)+'\n\n')
                duplication_list2.append(str(number)+':')
                duplication_list2.append(' '.join(list2)+'\n\n')
                number+=1
                i+=sum
                continue
            if pos==len(codewithtype2):
                i+=1
                pos=0
        duplication_str1=' '.join(duplication_list1)
        duplication_str2=' '.join(duplication_list2)
        return duplication_str1,duplication_str2
    
    def __readfile_sgl(self,file_path):
        with open(file_path, 'r', encoding=self.__decode) as file:
            code = file.read()
        return code

    def __readfile_mul(self,file_path_list):
        code_list=[]
        for file_path in file_path_list:
            code=self.__readfile(file_path)
            code_list.append(code)
        return code_list

    def __readfile_str1(self,code1,path1):
        match (code1,path1):
            case (None,None):raise ValueError("code1 or path1 should not be None")
            case (code,None):self.__code1=code
            case (None,path):
                match path:
                    case str():self.__code1=self.__readfile_sgl(path)
                    case _:raise ValueError("path1 should be str")
            case (_,_):raise ValueError("code1 and path1 should not be both not None")
    
    def __readfile_str2(self,code2,path2):
        match (code2,path2):
            case (None,None):raise ValueError("code2 or path2 should not be None")
            case (code,None):self.__code2=code
            case (None,path):
                match path:
                    case str():self.__code2=self.__readfile_sgl(path)
                    case _:raise ValueError("path2 should be str")
            case (_,_):raise ValueError("code2 and path2 should not be both not None")
    
    def __readfile_list(self,code2,path2):
        match (code2,path2):
                case (None,None):raise ValueError("code2 or path2 should not be None")
                case (code,None):self.__code2=code
                case (None,path):
                    match path:
                        case str():self.__code2=self.__readfile_sgl(path)
                        case list():self.__code2=self.__readfile_mul(path)
                        case _:raise ValueError("path2 should be str or list")
                case (_,_):raise ValueError("code2 and path2 should not be both not None")

    @staticmethod
    def __preprocessor1(code):
        i=code.find('#include')
        while i!=-1:
            j=code.find('\n',i+7)+1
            code=code[:i]+code[j:]
            i=code.find('#include')          
        return code
    
    def __preprocess_cpp_code(self,code,decode):
        with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as temp_file:
            temp_file.write(code.encode(decode))
            temp_file_path = temp_file.name

        try:
            result = subprocess.run([self.__processby, '-E', temp_file_path], capture_output=True, text=True, check=True)
            preprocessed_code = result.stdout
            def macro_preprocess(code):
                def macro(s,code):      ##
                    e=code.find('\n',s+2)+1
                    code_new=code[:s]+code[e:]
                    return code_new
                i=preprocessed_code.find('#')
                while i!=-1:
                    code=macro(i,code)
                    i=code.find('#')
                return code
            preprocessed_code=macro_preprocess(preprocessed_code)
            return preprocessed_code

        except subprocess.CalledProcessError as e:
            print(f"process error: {e.stderr}")
            return None

        finally:
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"delete temp file error: {e}")
        
    @staticmethod
    def __preprocessor2(code):

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

        code=namespace(code)
        code=brackets(code)
        
        return code

    def __preprocess_after(self,code):
        
        code_temp=self.__preprocessor1(code)
        code_temp=self.__preprocess_cpp_code(code_temp,self.__decode)
        code_temp=self.__preprocessor2(code_temp)
        return code_temp

    def __preprocess_before(self):
        def preprocess(code):
            code_temp=self.__preprocessor1(code)
            code_temp=self.__preprocess_cpp_code(code_temp,self.__decode)
            return code_temp
        
        self.__code1=preprocess(self.__code1)
        self.__code2=preprocess(self.__code2)
      
    def __ast_after(self,code):
        tree=self.__parser.parse(bytes(code, 'utf8'))
        root_node=tree.root_node
        ast_list=[]         #  node type list of ast
        def ast_dfs(node):
            # DFS
            nonlocal  ast_list
            # from cst to ast
            def traverse(node):
                children=node.children
                for child in node.children:
                    if child.type in ['{','}','[',']','(',')',';','\'','\"',',']:
                        children.remove(child)
                if len(children)==1:           #only one child
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
       
    def __cst_before(self,code):
        tree=self.__parser.parse(bytes(code, 'utf8'))
        root_node=tree.root_node
        node_list = []  # [(node_id, node_str), ...]
        edge_list = []  # [(parent_id, child_id), ...]
        codewithtype=[] # [(node_type,node_text), ...]
        def cst_dfs(node,parent_id=None):
            # DFS
            nonlocal node_list, edge_list
            node_id = str(len(node_list))
            node_type = node.type
            node_text = str(node.text.decode())
            node_str = node_type +'\n'+node_text
            node_list.append((node_id, node_str))
            if node.child_count==0:
                codewithtype.append((node_type,node_text))
            if parent_id is not None:
                edge_list.append((parent_id, node_id))
            # traverse children
            for child in node.children:
                cst_dfs(child,node_id)
        cst_dfs(root_node)
        return node_list,edge_list,codewithtype       

    @staticmethod
    def __draw_tree(node_list, edge_list):
        dot = Digraph()
        # draw nodes
        for node in node_list:
            dot.node(name=node[0], label=node[1], shape='box')
        # draw edges
        for edge in edge_list:
            dot.edge(tail_name=edge[0], head_name=edge[1], lable='')
        return dot
