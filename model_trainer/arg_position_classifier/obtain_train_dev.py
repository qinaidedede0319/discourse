import sys

sys.path.append("../../")
import json

import pickle
import util

import config
from connective import Connective
from parser_util import get_conn_name
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper
from model_trainer.NT_arg_extractor.NT_dict_util import get_sent_clauses



def get_SS_vs_PS_connective(relations_path, dest_dir):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    SS_counter = 0
    PS_counter = 0

    SS_connective_list = []
    PS_connective_list = []

    for relation in relations:
        if relation["Type"] =="Explicit":
            DocID = relation["DocID"]
            sent_index = relation["Connective"]["TokenList"][0][3]
            conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
            #需要将获取语篇连接词的头
            raw_connective = relation["Connective"]["RawText"]
            chm = ConnHeadMapper()
            conn_head, indices = chm.map_raw_connective(raw_connective)
            conn_head_indices = [conn_token_indices[index] for index in indices]

            Arg1_sent_indices = sorted([item[3] for item in relation["Arg1"]["TokenList"]])
            Arg2_sent_indices = sorted([item[3] for item in relation["Arg2"]["TokenList"]])

            # if len(set(Arg1_sent_indices)) == 1 and len(set(Arg2_sent_indices)) == 1:#只考虑句子长度为1
            if set(Arg2_sent_indices) >= set(Arg1_sent_indices) :#SS
                SS_counter += 1
                connective = Connective(DocID, sent_index, conn_head_indices, conn_head)
                connective.label = 0 # ss
                SS_connective_list.append(connective)

            else:
                if Arg1_sent_indices[-1] < Arg2_sent_indices[0] :# PS
                    PS_counter += 1
                    connective = Connective(DocID, sent_index, conn_head_indices, conn_head)
                    connective.label = 1 # ps
                    PS_connective_list.append(connective)

    connectives = SS_connective_list + PS_connective_list

    pickle.dump(connectives, open(dest_dir + "/ss_vs_ps_conn.pkl", "wb" ))


    print("Explicit: SS: %d.\tPS:%d" % (len(SS_connective_list), len(PS_connective_list)))


def print_instances_by_connective_name(conn_name):
    # relations_file = open(config.TRAIN_PATH + "/relations.json")
    # relations = [json.loads(x) for x in relations_file]
    # relations_file.close()
    #
    # parse_dict = json.load(open(config.TRAIN_PATH + "/parses.json"))

    relations_file = open(config.DEV_PATH + "relations.json")
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    parse_dict = json.load(open(config.DEV_PATH + "pdtb-parses.json"))

    PS_instances = []
    SS_instances = []

    for relation in relations:
        if relation["Type"] == "Explicit":
            DocID = relation["DocID"]
            sent_index = relation["Connective"]["TokenList"][0][3]
            conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
            # 需要将获取语篇连接词的头
            raw_connective = relation["Connective"]["RawText"]
            chm = ConnHeadMapper()
            conn_head, indices = chm.map_raw_connective(raw_connective)
            conn_head_indices = [conn_token_indices[index] for index in indices]

            this_conn_name = " ".join([parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0].lower()
                              for word_index in conn_head_indices])

            if this_conn_name != conn_name:
                continue

            Arg1_sent_indices = sorted([item[3] for item in relation["Arg1"]["TokenList"]])
            Arg2_sent_indices = sorted([item[3] for item in relation["Arg2"]["TokenList"]])


            if len(set(Arg1_sent_indices)) != 1 or len(set(Arg2_sent_indices)) != 1:#只考虑句子长度为1
                continue

            if set(Arg2_sent_indices) >= set(Arg1_sent_indices):  # SS

                sent = " ".join([word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]])

                instance = "==" * 40 + "\n"
                instance += "SS\n"
                instance += "%s %d %s\n" % (DocID, sent_index, " ".join(map(str, conn_head_indices)))
                instance += "sent: %s\n" % (sent)
                instance += "%s\n" % (conn_name)

                SS_instances.append(instance)

                pass
            else:
                if Arg1_sent_indices[-1] < Arg2_sent_indices[0]:  # PS

                    Arg1_sent_index = Arg1_sent_indices[-1]
                    Arg2_sent_index = Arg2_sent_indices[0]

                    Arg1_sent = " ".join([word[0] for word in parse_dict[DocID]["sentences"][Arg1_sent_index]["words"]])
                    Arg2_sent = " ".join([word[0] for word in parse_dict[DocID]["sentences"][Arg2_sent_index]["words"]])

                    instance = "==" * 40 + "\n"
                    instance += "PS\n"
                    instance += "%s %d %s\n" % (DocID, sent_index, " ".join(map(str, conn_head_indices)))
                    instance += "Arg1: %s\n" % (Arg1_sent)
                    instance += "Arg2: %s\n" % (Arg2_sent)
                    instance += "%s" % (conn_name)

                    PS_instances.append(instance)


    print("PS: %d; SS: %d" % (len(PS_instances), len(SS_instances)))

    print("\n".join(PS_instances))
    print("\n".join(SS_instances))





if __name__ == "__main__":

    relations_path = config.TRAIN_PATH + "relations.json"
    get_SS_vs_PS_connective(relations_path, config.DATA_PATH + "ss_vs_ps_conn/train")
    
    relations_path = config.DEV_PATH + "relations.json"
    get_SS_vs_PS_connective(relations_path, config.DATA_PATH + "ss_vs_ps_conn/dev")


    print_instances_by_connective_name("also")

    parse_dict = json.load(open(config.TRAIN_PATH + "pdtb-parses.json"))
    DocID = "wsj_0922"
    sent_index = 19
    # [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], [26, 27, 28]]
    sent_clauses = get_sent_clauses(parse_dict, DocID, sent_index)
    
    print(sent_clauses)
