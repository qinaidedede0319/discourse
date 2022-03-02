import sys
sys.path.append("../../")
import json
import pyprind
import pickle
import config
import util
from clause import Clause
from clauseArgument import ClauseArgument
from model_trainer.NT_arg_extractor.NT_dict_util import get_sent_clauses



def get_implicit_relations(relations_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    total = 0
    implicit_total = 0
    implicit_relations = []
    for relation in relations:
        total += 1

        # 只对 Implicit
        if relation["Type"] != "Implicit":
            continue

        arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
        arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

        # 只对都是单个句子的
        if len(set(arg1_sent_indices)) != 1 or len(set(arg2_sent_indices)) != 1:
            # print(DocID, set(arg1_sent_indices), set(arg2_sent_indices))
            continue

        implicit_total += 1
        implicit_relations.append(relation)

    print("Implicit/Total: %d/%d=%.4f" % (implicit_total, total, implicit_total/total))

    return implicit_relations


def get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg_sent_index, Arg_token_indices=None):


    # [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], [26, 27, 28]]
    # clause_list = get_sent_clauses_deeper(parse_dict, DocID, Arg_sent_index)
    # clause_list = get_sent_clauses_just_by_punctuation(parse_dict, DocID, Arg_sent_index)
    clause_list = get_sent_clauses(parse_dict, DocID, Arg_sent_index)

    # 因为Arg1中不存在连接词, 所以不用在分啦~~~~
    new_clause_list = clause_list

    # 重新去下两侧标点
    new_clause_list_no_punctuation = []
    for clause_indices in new_clause_list:
        index_word_list = [(index, parse_dict[DocID]["sentences"][Arg_sent_index]["words"][index][0]) \
                           for index in clause_indices]

        index_word_list = util.list_strip_punctuation(index_word_list)

        s = [index for index, word in index_word_list]
        if s != []:
            new_clause_list_no_punctuation.append(s)


    # 对 clause_list 进行封装
    clauses = []
    conll15_clauses = []

    for index, clause_indices in enumerate(new_clause_list_no_punctuation):

        if Arg_token_indices is None:
            label = None
        else:
            label = 0
            if set(Arg_token_indices) & set(clause_indices) != set([]):
                label = 1

        clause = Clause(DocID, Arg_sent_index, clause_indices, index)
        clause.label = label

        clauses.append(clause)
        conll15_clauses.append((clause_indices,""))


    for clause in clauses:
        clause.all_clauses = clauses
        clause.clauses = conll15_clauses


    clauseArgument = ClauseArgument(relationID, DocID, Arg_sent_index, clauses)

    return clauseArgument


def get_implicit_Arg1_clauseArguments_for_train(relations_path, parse_dict_path, dest_dir):

    parse_dict = json.load(open(parse_dict_path))
    implicit_relations = get_implicit_relations(relations_path)

    clauseArguments = []
    process_bar = pyprind.ProgPercent(len(implicit_relations))
    for relation in implicit_relations:
        process_bar.update()

        arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
        arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

        arg1_sent_index = arg1_sent_indices[0]
        arg2_sent_index = arg2_sent_indices[0]
        # 对于训练集合, 只考虑arg1 arg2 不在同一个句子的
        if arg1_sent_index == arg2_sent_index:
            continue

        relationID = relation["ID"]
        DocID = relation["DocID"]

        Arg1_sent_index = relation["Arg1"]["TokenList"][0][-2]
        Arg1_token_indices = [item[-1] for item in relation["Arg1"]["TokenList"]]

        clauseArgument = get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg1_sent_index, Arg1_token_indices)
        clauseArguments.append(clauseArgument)

    print("Implicit_Arg1_clauseArguments size: %d" % (len(clauseArguments)))
    pickle.dump(clauseArguments, open(dest_dir + "/implicit_arg1_vs_null_clauseArguments.pkl", "wb" ))



def get_implicit_Arg1_clauseArguments_for_dev(relations_path, parse_dict_path, dest_dir):

    parse_dict = json.load(open(parse_dict_path))
    implicit_relations = get_implicit_relations(relations_path)

    clauseArguments = []
    process_bar = pyprind.ProgPercent(len(implicit_relations))
    for relation in implicit_relations:
        process_bar.update()

        relationID = relation["ID"]
        DocID = relation["DocID"]

        Arg1_sent_index = relation["Arg1"]["TokenList"][0][-2]
        Arg1_token_indices = [item[-1] for item in relation["Arg1"]["TokenList"]]

        clauseArgument = get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg1_sent_index, Arg1_token_indices)
        clauseArguments.append(clauseArgument)

    print("Implicit_Arg1_clauseArguments size: %d" % (len(clauseArguments)))
    pickle.dump(clauseArguments, open(dest_dir + "/implicit_arg1_vs_null_clauseArguments.pkl", "wb" ))



def get_implicit_Arg1_clauseArguments_for_parser(parse_dict, NonEntRelRelations):

    clauseArguments = []
    # process_bar = pyprind.ProgPercent(len(NonEntRelRelations))
    for discourseRelation in NonEntRelRelations:
        # process_bar.update()

        relationID = discourseRelation.ID
        DocID = discourseRelation.DocID

        Arg1_sent_index = discourseRelation.Arg1_sent_index

        clauseArgument = get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg1_sent_index)
        clauseArguments.append(clauseArgument)

    return clauseArguments

if __name__ == "__main__":


    get_implicit_Arg1_clauseArguments_for_train(config.TRAIN_PATH + "relations.json", config.TRAIN_PATH + "pdtb-parses.json",
                                config.DATA_PATH + "implicit_arg1_vs_null/train")

    get_implicit_Arg1_clauseArguments_for_dev(config.DEV_PATH + "relations.json", config.DEV_PATH + "pdtb-parses.json",
                                config.DATA_PATH + "implicit_arg1_vs_null/dev")