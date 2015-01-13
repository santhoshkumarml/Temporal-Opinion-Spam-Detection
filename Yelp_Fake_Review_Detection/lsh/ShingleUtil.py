'''
Created on Jan 12, 2015

@author: santhosh
'''
import re
import numpy
import sys
skip_words = '[\n]|[ ]|[\t]'

def createAndReturnShingles(texts, n):
    shingle_dict = dict()
    text_index = 0
    for text in texts:
        shingle = ''
        for t in text:
            if t != ' ':
                shingle = shingle+t
            if(len(shingle) == n):
                if shingle not in shingle_dict:
                    shingle_dict[shingle] = numpy.zeros(len(texts))        
                shingle_dict[shingle][text_index] = 1
                shingle = ''
    
        if shingle != '':
            if shingle not in shingle_dict:
                    shingle_dict[shingle] = numpy.zeros(len(texts))
            shingle_dict[shingle][text_index] = 1
            
        text_index+=1
        
    return shingle_dict

def formDataMatrix(texts, n):
    shingle_dict = createAndReturnShingles(texts, n)
    
    n = len(shingle_dict.keys())
    m = len(texts)
    
    data_matrix = numpy.zeros(shape =(n,m))
    shingle_list = []
    
    index = 0
    for key in shingle_dict.keys():
        data_matrix[index] = shingle_dict[key]
        shingle_list.append(key)
        index+=1

    #print shingle_list, data_matrix
    return data_matrix
            