import sys
sys.path.append("../../")
import json
import pyprind
import pickle
import config
from model_trainer.Implicit_Arg1_extractor.obtain_train_dev import get_clauses_for_Implicit_Arg


def get_implicit_relations(relations_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    total = 0
    implicit_total = 0
    implicit_relations = []
    for relation in relations:
        total += 1
        if relation["Type"] != "Implicit":
            continue

        arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
        arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

        if len(set(arg1_sent_indices)) != 1 or len(set(arg2_sent_indices)) != 1:
            # print(DocID, set(arg1_sent_indices), set(arg2_sent_indices))
            continue


        implicit_total += 1
        implicit_relations.append(relation)

    print("Implicit/Total: %d/%d=%.4f" % (implicit_total, total, implicit_total/total))

    return implicit_relations




def get_implicit_Arg2_clauseArguments_for_train(relations_path, parse_dict_path, dest_dir):

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

        Arg2_sent_index = relation["Arg2"]["TokenList"][0][-2]
        Arg2_token_indices = [item[-1] for item in relation["Arg2"]["TokenList"]]

        clauseArgument = get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg2_sent_index, Arg2_token_indices)
        clauseArguments.append(clauseArgument)

    print("Implicit_Arg2_clauseArguments size: %d" % (len(clauseArguments)))
    pickle.dump(clauseArguments, open(dest_dir + "/implicit_arg2_vs_null_clauseArguments.pkl", "wb" ))



def get_implicit_Arg2_clauseArguments_for_dev(relations_path, parse_dict_path, dest_dir):

    parse_dict = json.load(open(parse_dict_path))
    implicit_relations = get_implicit_relations(relations_path)

    clauseArguments = []
    process_bar = pyprind.ProgPercent(len(implicit_relations))
    for relation in implicit_relations:
        process_bar.update()

        relationID = relation["ID"]
        DocID = relation["DocID"]

        Arg2_sent_index = relation["Arg2"]["TokenList"][0][-2]
        Arg2_token_indices = [item[-1] for item in relation["Arg2"]["TokenList"]]

        clauseArgument = get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg2_sent_index, Arg2_token_indices)
        clauseArguments.append(clauseArgument)

    print("Implicit_Arg2_clauseArguments size: %d" % (len(clauseArguments)))
    pickle.dump(clauseArguments, open(dest_dir + "/implicit_arg2_vs_null_clauseArguments.pkl", "wb" ))


def get_implicit_Arg2_clauseArguments_for_parser(parse_dict, NonEntRelRelations):

    clauseArguments = []
    # process_bar = pyprind.ProgPercent(len(NonEntRelRelations))
    for discourseRelation in NonEntRelRelations:
        # process_bar.update()

        relationID = discourseRelation.ID
        DocID = discourseRelation.DocID

        Arg2_sent_index = discourseRelation.Arg2_sent_index

        clauseArgument = get_clauses_for_Implicit_Arg(parse_dict, relationID, DocID, Arg2_sent_index)
        clauseArguments.append(clauseArgument)

    return clauseArguments

if __name__ == "__main__":

    get_implicit_Arg2_clauseArguments_for_train(config.TRAIN_PATH + "relations.json", config.TRAIN_PATH + "pdtb-parses.json",
                                config.DATA_PATH + "implicit_arg2_vs_null/train")

    get_implicit_Arg2_clauseArguments_for_dev(config.DEV_PATH + "relations.json", config.DEV_PATH + "pdtb-parses.json",
                                config.DATA_PATH + "implicit_arg2_vs_null/dev")