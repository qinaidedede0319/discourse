import string
from feature import Feature
from tools.PorterStemmer import PorterStemmer
from confusion_matrix import ConfusionMatrix
import os



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

''' 获取span在sentence中的indices,span在sentence中返回indices,否，返回[[2,3], [6,7]] '''
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

def get_mallet_gold_list(file_path):
    gold_list = []
    for line in open(file_path):
        gold = line.strip().split("\t")[0]
        gold_list.append(gold)
    return gold_list

def get_mallet_predicted_list(file_path):
    predicted_dict_list = read_mallet_output(file_path)
    predicted_list = []
    for predicted_dict in predicted_dict_list:
        sort_label = sorted(predicted_dict.items(), key=lambda x: x[1],reverse = True)
        predicted_list.append(sort_label[0][0])
    return predicted_list

def read_mallet_output(file_path):
        predicted_dict_list = []
        for line in open(file_path):
            fields = line.rstrip().split("\t")[1:]
            dict = {}
            for i in range(len(fields)):
                if i % 2 == 0:
                    dict[fields[i]] = float(fields[i+1])
            predicted_dict_list.append(dict)
        return predicted_dict_list

# gold_list = ['no', 'yes', 'no', 'yes', ...]
# predicted_list = ['yes', 'yes', 'no', 'yes', ...]
def compute_binary_eval_metric(predicted_list, gold_list, binary_alphabet):
    cm = ConfusionMatrix(binary_alphabet)
    for (predicted_span, gold_span) in zip( predicted_list, gold_list):
        cm.add(predicted_span, gold_span)
    return cm


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

# [1, 2, 44, 5, 6]
# [[1, 2], [44], [5, 6]]
def get_discontinuous_chunk(in_list):
    T = []
    tmp = []
    for i in range(len(in_list)):
        tmp.append(in_list[i])
        if i == len(in_list) - 1 or in_list[i]+1 != in_list[i+1]:
            T.append(tmp)
            tmp = []

    return T

def split_sentence_by_punctuation(words_list):
    punctuation = "...,:;?!~--"
    #先按标点符号分
    clause_indices_list = []
    temp = []
    for index, word in enumerate(words_list):
        if word not in punctuation:
            temp.append((index, word))
        if index == len(words_list) - 1 or words_list[index + 1] in punctuation:
            temp = list_strip_punctuation(temp)
            if temp:
                clause_indices_list.append([index for index, word in temp])
            temp = []

    return clause_indices_list

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

def listdir_no_hidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f
