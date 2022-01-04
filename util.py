import string
from feature import Feature
from tools.PorterStemmer import PorterStemmer


#Singleton，usage: @singleton...
def singleton(cls):
    instances = {}
    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

''' remove punctuation in string '''
def removePuctuation(s):
    exclude = string.punctuation + "``" + "''"
    s = ''.join(ch for ch in s if ch not in exclude)
    return s

# key : index
def load_dict_from_file(dict_file_path):
    dict = {}
    dict_file = open(dict_file_path)
    lines = [line.strip() for line in dict_file]
    for index, line in enumerate(lines):
        if line == "":
            continue
        dict[line] = index+1
    dict_file.close()
    return dict

def load_list_from_file(list_file_path):
    list_file = open(list_file_path)
    list = [line.strip() for line in list_file]
    return list

def getSpanIndecesInSent(span_tokens, sent_tokens):
    indice = []
    span_length = len(span_tokens); sent_length = len(sent_tokens)
    for i in range(len(sent_tokens)):
        if (i+span_length) <= sent_length  and sent_tokens[i:i+span_length] == span_tokens:
            indice.append(list(range(i,i+span_length)))
    return indice

# merge all the features in the feature_list
def mergeFeatures(feature_list, name = ""):
    dimension = 0
    feat_string = ""
    for feature in feature_list:
        if dimension == 0:# first one
            feat_string = feature.feat_string
        else:
            if feature.feat_string != "":
                # change the indices of the current feature.
                temp = ""
                for item in feature.feat_string.split(" "):
                    index, value = item.split(":")
                    temp += " %d:%s" % (int(index)+dimension, value)
                feat_string += temp
        dimension += feature.dimension

    merged_feature = Feature(name, dimension,{})
    merged_feature.feat_string = feat_string.strip()
    return merged_feature

def write_example_list_to_file(example_list, to_file):
    to_file = open(to_file, "w")
    to_file.write("\n".join([example.content + " # " + example.comment for example in example_list]))
    to_file.close()

def list_strip_punctuation(list):
    punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~""" + "``" + "''"
    i = 0
    while i < len(list) and list[i][1] in punctuation + "-LCB--LRB-":
        i += 1
    if i == len(list):
        return []

    j = len(list) - 1
    while j >= 0 and list[j][1] in punctuation + "-RRB--RCB-":
        j -= 1

    return list[i: j+1]

def get_compressed_path(path):
    list = path.split("-->")
    temp = []
    for i in range(len(list)):
        if i+1 < len(list) and list[i] != list[i+1] :
            temp.append(list[i])
        if i+1 == len(list):
            temp.append(list[i])
    return "-->".join(temp)

def stem_string(line):
    if line == "":
        return ""
    p = PorterStemmer()
    word = ""
    output = ""
    for c in line:
        if c.isalpha():
            word += c.lower()
        else:
            if word:
                output += p.stem(word, 0,len(word)-1)
                word = ''
            output += c.lower()
    if word:
        output += p.stem(word, 0,len(word)-1)
    return output

def cross_product(list1, list2):
    t = []
    for i in list1:
        for j in list2:
            t.append(i * j)
    return t