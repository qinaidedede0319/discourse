import util
from connective_dict import Connectives_dict
from example import Example
import config, os, json
import model_trainer.mallet_util as mallet_util
from connective import Connective
from syntax_tree import Syntax_tree
from model_trainer.NT_arg_extractor.constituent import Constituent


# identify connectives in sentence (sent_tokens)
# return indices: [[2, 3], [0]]
def _check_connectives(sent_tokens):
    sent_tokens = [word.lower() for word in sent_tokens ]
    indices = []
    tagged = set([])
    sortedConn = Connectives_dict().sorted_conns_list
    for conn in sortedConn:
        if '..' in conn:
            c1, c2 = conn.split('..')
            c1_indice = util.getSpanIndecesInSent(c1.split(), sent_tokens)#[[7]]
            c2_indice = util.getSpanIndecesInSent(c2.split(), sent_tokens)#[[10]]
            if c1_indice!= [] and c2_indice != []:
                if c1_indice[0][0] < c2_indice[0][0]:
                    temp = set([t for t in (c1_indice[0]+c2_indice[0]) ])
                    if tagged & temp == set([]):
                        indices.append(c1_indice[0]+c2_indice[0])# [[7], [10]]
                        tagged = tagged.union(temp)
        else:
            c_indice = util.getSpanIndecesInSent(conn.split(), sent_tokens)#[[2,6],[1,3],...]
            if c_indice !=[]:
                tt = []
                for item in c_indice:
                    if set(item) & tagged == set([]):
                        tt.append(item)
                c_indice = tt

                if c_indice != []:
                    indices.extend([item for item in c_indice])#[([2,6], 'for instance'), ....]
                    tagged = tagged.union(set([r for t in c_indice for r in t]))
    return indices

def _get_doc_conns(document):
    list = [] #[(sent_index, conn_indices), ()..]
    for sent_index, sentence in enumerate(document["sentences"]):
        sent_words_list = [word[0] for word in sentence["words"]]
        for conn_indices in _check_connectives(sent_words_list): #[[2, 3], [0]]
            list.append((sent_index, conn_indices))
    return list

def get_all_connectives(documents):
    conns_list = [] #[(DocID, sent_index, conn_indices), ()..]
    for DocID in documents:
        doc = documents[DocID]
        list = _get_doc_conns(doc) #[(sent_index, conn_indices), ()..]
        for sent_index, conn_indices in list:
            conns_list.append((DocID, sent_index, conn_indices))
    return conns_list

def getParagTexts(raw_file):
        text = [line.strip() for line in raw_file.readlines()]+['']
        t = 0
        for line in text:
            if line == '.START' or line == "":
                t += 1
            else:
                break
        text = text[t:]

        paragTexts =[]
        paragText = ""
        for line in text:
            if line != '':
                paragText += line.replace(" ", "")
            else:
                if paragText != "":
                    paragText = util.removePuctuation(paragText)
                    paragTexts.append(paragText)
                    paragText = ""
        return paragTexts

#[(DocID, sent_index, conn_indices), ()..]
def conn_clf_print_feature(parse_dict, conns_list, feature_function, to_file):

    print("\tExtract features: [..]")
    example_list = []
    for DocID, sent_index, conn_indices in conns_list:
        feature = feature_function(parse_dict, DocID, sent_index, conn_indices)
        example = Example("", feature)
        example_list.append(example)
    # write example_list to file
    util.write_example_list_to_file(example_list, to_file)
    print ("\r\tExtract features: [OK]")

def conn_clf_read_model_output(conn_clf_model_output, conns_list):
    # ['yes', 'no'...]
    pred_list = mallet_util.get_mallet_predicted_list(conn_clf_model_output)
    disc_conns = []
    for pred, conn in zip(pred_list, conns_list):
        if pred == "1":
            disc_conns.append(conn)
    return disc_conns

def getParagIndex(paragTexts, sent_tokens):
    paragIndex = -1
    sent = "".join(sent_tokens)
    sent = sent.replace("-LCB-", "")
    sent = sent.replace("-LRB-", "")
    sent = sent.replace("-RCB-", "")
    sent = sent.replace("-RRB-", "")
    sent = util.removePuctuation(sent)


    matchedParag = set([])
    for index, paragText in enumerate(paragTexts):
        if sent in paragText:
            matchedParag.add(index)

    #matchedParag might be [1],[3,6] , take the minimum
    if matchedParag != set([]):
        paragIndex = min(matchedParag)
        # remove the sent which have been matched
        paragTexts[paragIndex] = paragTexts[paragIndex].replace(sent, "", 1)

    # if paragIndex == -1:
    #     print sent_tokens
    #     raise ValueError("sentence : '%s' , can not get the paragIndex" % (sent) )


    return paragIndex

def add_paragraph_info_for_parse(parse_dict, raw_path):
    for DocID in parse_dict:
        try:
            raw_file = open("%s/%s" % (raw_path, DocID), encoding='utf-8', errors='ignore')
            # raw_file = codecs.open("%s/%s" % (raw_path, DocID), encoding="utf-8", errors="ignore")

            paragTexts = getParagTexts(raw_file)# ["IamaDoy","asas']
            for sent_index in range(len(parse_dict[DocID]["sentences"])):
                sent_words_list = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
                ParagIndex = getParagIndex(paragTexts, sent_words_list)
                parse_dict[DocID]["sentences"][sent_index]["paragraph"] = ParagIndex

        except IOError:
            # if failed, set parse_dict[DocID]["sentences"][sent_index]["paragraph"] = -1
            for sent_index in range(len(parse_dict[DocID]["sentences"])):
                parse_dict[DocID]["sentences"][sent_index]["paragraph"] = -1

def put_feature_to_model(feature_path, model_path, model_output_path):
    cmd = config.MALLET_PATH + "/bin/mallet classify-file --input " + feature_path + " --output " + model_output_path + " --classifier " + model_path
    os.system(cmd)

def arg_position_print_feature(parse_dict, conns_list, feature_function, to_file):

    print ("\tExtract features: [..]")
    example_list = []
    for DocID, sent_index, conn_indices in conns_list:
        feature = feature_function(parse_dict, DocID, sent_index, conn_indices)
        example = Example("", feature)
        example_list.append(example)
    # write example_list to file
    util.write_example_list_to_file(example_list, to_file)
    print ("\r\tExtract features: [OK]")

def arg_position_print_feature(parse_dict, conns_list, feature_function, to_file):

    print ("\tExtract features: [..]")
    example_list = []
    for DocID, sent_index, conn_indices in conns_list:
        feature = feature_function(parse_dict, DocID, sent_index, conn_indices)
        example = Example("", feature)
        example_list.append(example)
    # write example_list to file
    util.write_example_list_to_file(example_list, to_file)
    print ("\r\tExtract features: [OK]")

def arg_position_read_model_output(arg_position_model_output, conns_list):
    SS_conns_list = []
    PS_conns_list = []
    # ['SS', 'PS'...]
    pred_list = mallet_util.get_mallet_predicted_list(arg_position_model_output)
    for pred, conn in zip(pred_list, conns_list):
        if config.LABEL_TO_ARG_POSITION[pred] == "SS":
            SS_conns_list.append(conn)
        if config.LABEL_TO_ARG_POSITION[pred] == "PS":
            PS_conns_list.append(conn)

    return SS_conns_list, PS_conns_list

def divide_SS_conns_list(SS_conns_list):
    SS_conns_parallel_list = []
    SS_conns_not_parallel_list = []
    for conn in SS_conns_list:
        DocID, sent_index, conn_indices = conn
        parallel = False
        if len(conn_indices) > 1:
            for i in range(len(conn_indices)):
                if i + 1 < len(conn_indices) and conn_indices[i+1] - conn_indices[i] > 1:
                    parallel = True
        if parallel:
            SS_conns_parallel_list.append(conn)
        else:
            SS_conns_not_parallel_list.append(conn)

    return SS_conns_parallel_list, SS_conns_not_parallel_list

def get_all_connectives_for_NT(parse_dict, conns_list):
    connectives = []
    for index, conn in enumerate(conns_list):
        # turn to connective object
        DocID, sent_index, conn_indices = conn
        conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)
        connective = Connective(DocID, sent_index, conn_indices, conn_name)
        connective.relation_ID = index
        connectives.append(connective)
    return connectives

def get_conn_name(parse_dict, DocID, sent_index, conn_indices):
    # obtain the name of the connective
    conn_name = " ".join([parse_dict[DocID]["sentences"][sent_index]["words"][word_token][0] \
                  for word_token in conn_indices ])
    return conn_name.lower()

def get_Args_for_SS_parallel_conns(parse_dict, SS_conns_parallel_list):
    temp = []
    source = "SS"
    for conn in SS_conns_parallel_list:
        DocID, sent_index, conn_indices = conn
        if len(conn_indices) == 2:# if then ,either or, neither nor
            conn_1_index = conn_indices[0]
            conn_2_index = conn_indices[1]

            Arg1 = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) \
                        for index in range(conn_1_index+1, conn_2_index)]

            sent_length = len(parse_dict[DocID]["sentences"][sent_index]["words"])
            Arg2 = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) \
                        for index in range(conn_2_index+1, sent_length)]

            Arg1 = util.list_strip_punctuation(Arg1)
            Arg2 = util.list_strip_punctuation(Arg2)

            Arg1 = [item[0] for item in Arg1]
            Arg2 = [item[0] for item in Arg2]

            temp.append((source, DocID, sent_index, conn_indices, Arg1, Arg2))

        elif len(conn_indices) == 8:# on the one hand on the other hand
            conn_1_index = conn_indices[3]
            conn_2_index = conn_indices[7]

            Arg1 = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) \
                        for index in range(conn_1_index+1, conn_2_index)]

            sent_length = len(parse_dict[DocID]["sentences"][sent_index]["words"])
            Arg2 = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) \
                        for index in range(conn_2_index+1, sent_length)]

            Arg1 = util.list_strip_punctuation(Arg1)
            Arg2 = util.list_strip_punctuation(Arg2)

            Arg1 = [item[0] for item in Arg1]
            Arg2 = [item[0] for item in Arg2]

            temp.append((source, DocID, sent_index, conn_indices, Arg1, Arg2))

    return temp

def constituent_print_feature(parse_dict, connectives, feature_function, to_file):

    print ("\tExtract features: [..]")

    example_list = []

    # total = float(len(connectives))
    for curr_index, connective in enumerate(connectives):
        # print "process: %.2f%%.\r" % ((curr_index + 1)/total*100),

        constituents = _get_constituents(parse_dict, connective)
        constituents = sorted(constituents, key=lambda constituent: constituent.indices[0])   # sort by age
        # extract features for each constituent
        for i, constituent in enumerate(constituents):
            feature = feature_function(parse_dict, constituent, i, constituents)
            example = Example("", feature)
            example.comment = "%s|%s" % (constituent.connective.relation_ID, " ".join([str(t) for t in constituent.get_indices()]))
            example_list.append(example)
    # write example_list to file
    util.write_example_list_to_file(example_list, to_file)

    print ("\r\tExtract features: [OK]")

def _get_constituents(parse_dict, connective):
    DocID = connective.DocID
    sent_index = connective.sent_index
    parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)
    if syntax_tree.tree == None:
        return []

    conn_indices = connective.token_indices
    constituent_nodes = []
    if len(conn_indices) == 1:# like and or so...
        conn_node = syntax_tree.get_leaf_node_by_token_index(conn_indices[0]).up
    else:
        conn_node = syntax_tree.get_common_ancestor_by_token_indices(conn_indices)
        conn_leaves = set([syntax_tree.get_leaf_node_by_token_index(conn_index) for conn_index in conn_indices])
        children = conn_node.get_children()
        for child in children:
            leaves = set(child.get_leaves())
            if conn_leaves & leaves == set([]):
                constituent_nodes.append(child)

    curr = conn_node
    while not curr.is_root():
        constituent_nodes.extend(syntax_tree.get_siblings(curr))
        curr = curr.up

    # obtain the Constituent object according to the node.
    constituents = []
    for node in constituent_nodes:
        cons = Constituent(syntax_tree, node)
        cons.connective = connective
        constituents.append(cons)
    return constituents

def constituent_read_model_output(
        constituent_feat_path, constituent_model_output, parse_dict, conns_list):

    feat_file = open(constituent_feat_path)
    pred_list = mallet_util.get_mallet_predicted_list(constituent_model_output)

    feature_list = [line.strip() for line in feat_file]

    # relation_dict[relation_ID] = {(['1', '2'],'Arg1')....}
    relation_dict = {}
    for feature_line, predicted in zip(feature_list, pred_list):
        comment = feature_line.split("#")[1].strip()
        relation_ID = int(comment.split("|")[0].strip())
        constituent_indices = comment.split("|")[1].strip().split(" ")
        if relation_ID not in relation_dict:
            relation_dict[relation_ID] = [(constituent_indices, predicted)]
        else:
            relation_dict[relation_ID].append((constituent_indices, predicted))
    # merge arg1(arg2) for each relation
    # relation_dict[relation_ID] = ([0,1],[2,3])
    for relation_ID in relation_dict.keys():
        list = relation_dict[relation_ID]
        Arg1_list = []
        Arg2_list = []
        for span, label in list:
            if label == "Arg1":
                Arg1_list.extend(span)
            if label == "Arg2":
                Arg2_list.extend(span)

        Arg1_list = sorted([int(item) for item in Arg1_list])
        Arg2_list = sorted([int(item) for item in Arg2_list])

        relation_dict[relation_ID] = (Arg1_list, Arg2_list)

    temp = []
    source = "SS"
    for i, conn in enumerate(conns_list):
        DocID, sent_index, conn_indices = conn

        Arg1_list, Arg2_list = relation_dict[i]

        Arg1_list = merge_NT_Arg(Arg1_list, parse_dict, DocID, sent_index)
        Arg2_list = merge_NT_Arg(Arg2_list, parse_dict, DocID, sent_index)

        if Arg1_list != [] and Arg2_list != []:
            temp.append((source, DocID, sent_index, conn_indices, Arg1_list, Arg2_list))
        else:
            pass
            # Arg1 or Arg2 is not identified
            # temp.append((source, DocID, sent_index, conn_indices, Arg1_list, Arg2_list))
            # if Arg1_list == []:
            #     print "Arg1###" + DocID, sent_index, conn_indices
            # if Arg2_list == []:
            #     print "Arg2###" + DocID, sent_index, conn_indices
            # if Arg1_list == [] and Arg2_list == []:
            #     print "Both###" + DocID, sent_index, conn_indices


    return temp

def merge_NT_Arg(Arg_list, parse_dict, DocID, sent_index):
    punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~""" + "``" + "''"
    if len(Arg_list) <= 1:
        return Arg_list
    temp = []
    # scan the missing parts, if it is the punctuation, then make up
    for i, item in enumerate(Arg_list):
        if i <= len(Arg_list) - 2:
            temp.append(item)
            next_item = Arg_list[i + 1]
            if next_item - item > 1:
                flag = 1
                for j in range(item + 1, next_item):
                    if parse_dict[DocID]["sentences"][sent_index]["words"][j][0] not in punctuation:
                        flag = 0
                        break
                if flag == 1:# make up
                    temp += range(item + 1, next_item)
    temp.append(Arg_list[-1])

    Arg = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in temp]
    # remove the leading or tailing punctuations
    Arg = util.list_strip_punctuation(Arg)

    Arg = [item[0] for item in Arg]

    return Arg