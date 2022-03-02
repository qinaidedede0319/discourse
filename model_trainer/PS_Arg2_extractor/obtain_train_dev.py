import sys
sys.path.append("../../")
import json
from collections import Counter
import pyprind
import pickle

import config
import util
from clause import Clause
from clauseArgument import ClauseArgument
from connective import Connective
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper
from model_trainer.NT_arg_extractor.NT_dict_util import get_sent_clauses_deeper
from parser_util import get_conn_name



def get_PS_relations(relations_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()


    explicit_total = 0
    PS_count = 0

    PS_relations = []
    for relation in relations:
        if relation["Type"] =="Explicit":
            explicit_total += 1

            conn_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Connective"]["TokenList"]]

            Arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
            Arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

            # 只考虑 Arg1，Arg2 均为单个句子的情况
            if len(set(Arg1_sent_indices)) == 1 and len(set(Arg2_sent_indices)) == 1:
                pass
            else:
                continue


            Arg1_sent_index, Arg2_sent_index = Arg1_sent_indices[0], Arg2_sent_indices[0]
            conn_sent_index = conn_sent_indices[0]

            # PS
            # if Arg2_sent_index == conn_sent_index and Arg1_sent_index < conn_sent_index:
            #     PS_count += 1
            #     PS_relations.append(relation)

            # IPS
            if Arg2_sent_index == conn_sent_index and Arg1_sent_index == conn_sent_index - 1:
                PS_count += 1
                PS_relations.append(relation)


    print("PS/Total: %d/%d=%.4f" % (PS_count, explicit_total, PS_count/explicit_total))

    return PS_relations

def get_clauseArgument_for_Arg2(parse_dict, relationID, DocID, sent_index, conn_indices, Arg2_token_indices=None):


    # [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], [26, 27, 28]]
    clause_list = get_sent_clauses_deeper(parse_dict, DocID, sent_index)

    # 因为Arg2中存在连接词, 所以按连接词分
    # 对于使用连接词分的, 感觉可以连接起来呢?!!!
    new_clause_list = []
    for clause_indices in clause_list:
        # 使用连接词断开的, 继续连里来!!!
        if set(clause_indices) & set(conn_indices) != set([]):
            left = list(sorted(set(clause_indices) - set(conn_indices)))
            if left != []:
                # 对于断开的, 去掉两侧的标点,再连起来
                left_chunk = util.get_discontinuous_chunk(left)
                _left = []
                for chunk in left_chunk:
                    index_word_list = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) \
                           for index in chunk]

                    index_word_list = util.list_strip_punctuation(index_word_list)

                    s = [index for index, word in index_word_list]
                    if s != []:
                        _left += s

                new_clause_list.append(list(sorted(_left)))
        else:
            new_clause_list.append(clause_indices)

    # 重新去下两侧标点
    new_clause_list_no_punctuation = []
    for clause_indices in new_clause_list:
        index_word_list = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) \
                           for index in clause_indices]

        index_word_list = util.list_strip_punctuation(index_word_list)

        s = [index for index, word in index_word_list]
        if s != []:
            new_clause_list_no_punctuation.append(s)


    # 对 clause_list 进行分装
    conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)

    connective = Connective(DocID, sent_index, conn_indices, conn_name)
    clauses = []
    conll15_clauses = []

    for index, clause_indices in enumerate(new_clause_list_no_punctuation):

        if Arg2_token_indices is None:
            label = None
        else:
            label = 0
            if set(Arg2_token_indices) & set(clause_indices) != set([]):
                label = 1

        clause = Clause(DocID, sent_index, clause_indices, index)
        clause.label = label
        clause.connective = connective

        clauses.append(clause)
        conll15_clauses.append((clause_indices,""))

    for clause in clauses:
        clause.all_clauses = clauses
        clause.clauses = conll15_clauses



    clauseArgument = ClauseArgument(relationID, DocID, sent_index, clauses)

    # words = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
    # print("==" * 40)
    # print(DocID, sent_index)
    # print(" ".join(words))
    # for clause_indices in new_clause_list_no_punctuation:
    #     clause = " ".join([words[index] for index in clause_indices])
    #     print(clause)
    #
    # print(new_clause_list_no_punctuation)

    return clauseArgument




def get_PS_Arg2_clauseArguments(relations_path, parse_dict_path, dest_dir):

    parse_dict = json.load(open(parse_dict_path))
    PS_relations = get_PS_relations(relations_path)


    clauseArguments = []

    process_bar = pyprind.ProgPercent(len(PS_relations))
    for relation in PS_relations:
        process_bar.update()

        relationID = relation["ID"]
        DocID = relation["DocID"]
        sent_index = relation["Connective"]["TokenList"][0][-2]

        conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
        #需要将获取语篇连接词的头
        raw_connective = relation["Connective"]["RawText"]
        chm = ConnHeadMapper()
        conn_head, indices = chm.map_raw_connective(raw_connective)
        conn_head_indices = [conn_token_indices[index] for index in indices]

        Arg2_token_indices = [item[-1] for item in relation["Arg2"]["TokenList"]]

        clauseArgument = get_clauseArgument_for_Arg2(parse_dict, relationID, DocID, sent_index, conn_head_indices, Arg2_token_indices)
        clauseArguments.append(clauseArgument)

    print("PS_Arg2_clauseArguments size: %d" % (len(clauseArguments)))
    pickle.dump(clauseArguments, open(dest_dir + "/ps_arg2_vs_null_clauseArguments.pkl", "wb" ))


def get_PS_Arg2_clauseArguments_for_parser(parse_dict, PS_connectives):

    clauseArguments = []

    # process_bar = pyprind.ProgPercent(len(PS_connectives))
    for connective in PS_connectives:
        # process_bar.update()

        relationID = connective.relationID
        DocID = connective.DocID
        conn_sent_index = connective.sent_index
        conn_head_indices = connective.conn_indices

        # PS Arg2 与 connective 在同一个句子
        clauseArgument = \
            get_clauseArgument_for_Arg2(parse_dict, relationID, DocID, conn_sent_index, conn_head_indices)
        clauseArguments.append(clauseArgument)

    return clauseArguments


if __name__ == "__main__":
    # get_PS_relations(config.TRAIN_PATH + "/relations.json")
    # get_PS_relations(config.DEV_PATH + "/relations.json")

    get_PS_Arg2_clauseArguments(config.TRAIN_PATH + "relations.json", config.TRAIN_PATH + "pdtb-parses.json",
                                config.DATA_PATH + "ps_arg2_vs_null/train")

    get_PS_Arg2_clauseArguments(config.DEV_PATH + "relations.json", config.DEV_PATH + "pdtb-parses.json",
                                config.DATA_PATH + "ps_arg2_vs_null/dev")