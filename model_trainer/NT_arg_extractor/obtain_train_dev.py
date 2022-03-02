import sys
sys.path.append("../../")
import json
import pickle
from collections import Counter
import config
from connective import Connective
from model_trainer.NT_arg_extractor.constituent import Constituent
from model_trainer.NT_arg_extractor.constituentArgument import ConstituentArgument
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper
from syntax_tree import Syntax_tree
from parser_util import get_conn_name



def Explicit_arguments_case_distribution(relations_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    explicit_total = 0

    cross_sentence_conn_counter = 0
    arg_sent_length_counter = Counter()

    # 两个argument同时不跨句子
    both_arg_in_one_sentence_count = 0

    #
    SS_count = 0
    PS_count = 0
    FS_count = 0

    PS_Arg1_distance_counter = Counter()


    for relation in relations:
        if relation["Type"] =="Explicit":
            explicit_total += 1

            DocID = relation["DocID"]

            conn_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Connective"]["TokenList"]]
            if len(set(conn_sent_indices)) > 1:
                cross_sentence_conn_counter += 1

            Arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
            Arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

            arg_sent_length_counter[len(set(Arg1_sent_indices))] += 1
            arg_sent_length_counter[len(set(Arg2_sent_indices))] += 1

            if len(set(Arg1_sent_indices)) == 1 and len(set(Arg2_sent_indices)) == 1:
                both_arg_in_one_sentence_count += 1
            else:
                continue

            # 只考虑 Arg1，Arg2 均为单个句子的情况

            Arg1_sent_index, Arg2_sent_index = Arg1_sent_indices[0], Arg2_sent_indices[0]
            conn_sent_index = conn_sent_indices[0]

            if Arg1_sent_index == conn_sent_index and Arg2_sent_index == conn_sent_index:
                SS_count += 1
            elif Arg2_sent_index == conn_sent_index and Arg1_sent_index < conn_sent_index:
                PS_count += 1

                PS_Arg1_distance_counter[conn_sent_index - Arg1_sent_index] += 1

            elif Arg2_sent_index == conn_sent_index and Arg1_sent_index > conn_sent_index:
                FS_count += 1
            else:
                print(Arg1_sent_index, Arg2_sent_index, conn_sent_index)


    print("cross_sentence_conn_counter: %d" % cross_sentence_conn_counter)

    print("==" * 40)
    print("arg_sent_length_counter")
    print("==" * 40)
    for arg_sent_length, freq in arg_sent_length_counter.most_common():
        print("%d: %d" % (arg_sent_length, freq))

    print("==" * 40)
    print("两个argument同时不跨句子: %d/%d\n" % (both_arg_in_one_sentence_count, explicit_total))

    print("SS: %d, PS: %d, FS: %d" % (SS_count, PS_count, FS_count))


    print("PS_Arg1_distance_counter")
    for PS_Arg1_distance, freq in PS_Arg1_distance_counter.most_common():
        print("%d: %d" % (PS_Arg1_distance, freq))



def get_Explicit_SS_connectives(relations_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()


    SS_connectives = []

    for relation in relations:
        if relation["Type"] =="Explicit":
            DocID = relation["DocID"]

            conn_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Connective"]["TokenList"]]
            if len(set(conn_sent_indices)) > 1:
                continue

            conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
            #需要将获取语篇连接词的头
            raw_connective = relation["Connective"]["RawText"]
            chm = ConnHeadMapper()
            conn_head, indices = chm.map_raw_connective(raw_connective)
            conn_head_indices = [conn_token_indices[index] for index in indices]

            Arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
            Arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

            Arg1_token_indices = [word_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
            Arg2_token_indices = [word_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

            # 只考虑 Arg1，Arg2 均为单个句子的情况
            if len(set(Arg1_sent_indices)) != 1 or len(set(Arg2_sent_indices)) != 1:
                continue
            Arg1_sent_index, Arg2_sent_index = Arg1_sent_indices[0], Arg2_sent_indices[0]
            conn_sent_index = conn_sent_indices[0]

            if Arg1_sent_index == conn_sent_index and Arg2_sent_index == conn_sent_index:

                # 不考虑平行连接词 on the one hand on the other hand

                if conn_head == "if then" or conn_head == "either or" \
                    or conn_head == "neither nor" or conn_head == "on the one hand on the other hand":
                    continue
                # if len(conn_head_indices) > 1:
                # print("-".join(map(str, [DocID, conn_sent_index, conn_head_indices, Arg1_token_indices, Arg2_token_indices])))
                connective = Connective(DocID, conn_sent_index, conn_head_indices, conn_head)
                connective.relationID = relation["ID"]
                connective.Arg1_token_indices = Arg1_token_indices
                connective.Arg2_token_indices = Arg2_token_indices
                SS_connectives.append(connective)

    print("SS: %d" % (len(SS_connectives)))
    return SS_connectives


def get_constituentArgument(parse_dict, relationID, DocID, sent_index, conn_indices, gold_Arg_token_indices=None, arg="arg1"):
    parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)
    # connective
    conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)
    connective = Connective(DocID, sent_index, conn_indices,conn_name)
    if syntax_tree.tree == None:
        return ConstituentArgument(relationID, DocID, sent_index, connective, [])

    conn_indices = conn_indices
    constituent_nodes = []
    if len(conn_indices) == 1:# like and or so...
        conn_node = syntax_tree.get_leaf_node_by_token_index(conn_indices[0]).up
    else:
        conn_node = syntax_tree.get_common_ancestor_by_token_indices(conn_indices)
        conn_leaves = set([syntax_tree.get_leaf_node_by_token_index(conn_index) for conn_index in conn_indices])
        for child in conn_node.get_children():
            if child.name == "SBAR":
                for x in child.get_children():
                    leaves = set(x.get_leaves())
                    if conn_leaves & leaves == set([]):
                        constituent_nodes.append(x)
            else:
                leaves = set(child.get_leaves())
                if conn_leaves & leaves == set([]):
                    constituent_nodes.append(child)

    curr = conn_node
    while not curr.is_root():
        constituent_nodes.extend(syntax_tree.get_siblings(curr))
        curr = curr.up

    gold_Arg_leaves = None
    if gold_Arg_token_indices is not None:
        gold_Arg_leaves = set([syntax_tree.get_leaf_node_by_token_index(index) for index in gold_Arg_token_indices])

    # 对 constituent_nodes 进行排序
    constituent_nodes = sorted(constituent_nodes, key=lambda node: syntax_tree.get_leaves_indices(node)[0])
    #根据node生成Constituent对象，并标记
    constituents = []
    for index, node in enumerate(constituent_nodes):
        constituent = Constituent(syntax_tree, node)
        constituent.connective = connective

        if gold_Arg_leaves is not None:
            node_leaves = set(node.get_leaves())
            if node_leaves & gold_Arg_leaves != set([]):
                if arg == "arg1":
                    label = 1
                else:
                    label = 2
            else:
                label = 0
            constituent.label = label
        else:
            constituent.label = None

        constituents.append(constituent)

    for constituent in constituents:
        constituent.all_constituents = constituents

    constituentArgument = ConstituentArgument(relationID, DocID, sent_index, connective, constituents)

    return constituentArgument


def get_SS_Arg_constituentArguments(relations_path, parse_dict_path, dest_dir):

    parse_dict = json.load(open(parse_dict_path))

    SS_connectives = get_Explicit_SS_connectives(relations_path)

    constituentArguments = []

    # 为每个连接词, 获取constituent
    for connective in SS_connectives:
        relationID = connective.relationID
        DocID = connective.DocID
        sent_index = connective.sent_index
        conn_indices = connective.token_indices

        # for Arg1
        Arg1_token_indices = connective.Arg1_token_indices

        constituentArgument = get_constituentArgument(parse_dict, relationID, DocID, sent_index, conn_indices, Arg1_token_indices, arg="arg1")

        constituentArguments.append(constituentArgument)

        # for Arg2
        Arg2_token_indices = connective.Arg2_token_indices

        constituentArgument = get_constituentArgument(parse_dict, relationID, DocID, sent_index, conn_indices, Arg2_token_indices, arg="arg2")

        constituentArguments.append(constituentArgument)


    print("SS_Arg12_constituentArguments size: %d" % (len(constituentArguments)))
    pickle.dump(constituentArguments, open(dest_dir + "/ss_arg12_vs_null_constituentArguments.pkl", "wb" ))



def get_SS_constituentArguments_for_parser(parse_dict, SS_connectives):
    constituentArguments = []
    # 为每个连接词, 获取constituent
    for connective in SS_connectives:
        relationID = connective.relationID
        DocID = connective.DocID
        sent_index = connective.sent_index
        conn_indices = connective.conn_indices

        constituentArgument = get_constituentArgument(parse_dict, relationID, DocID, sent_index, conn_indices)

        constituentArguments.append(constituentArgument)

    return constituentArguments


if __name__ == "__main__":
    pass
    get_SS_Arg_constituentArguments(config.TRAIN_PATH + "relations.json", config.TRAIN_PATH + "pdtb-parses.json",
                                  config.DATA_PATH + "ss_arg12_vs_null/train")

    get_SS_Arg_constituentArguments(config.DEV_PATH + "relations.json", config.DEV_PATH + "pdtb-parses.json",
                                  config.DATA_PATH + "ss_arg12_vs_null/dev")