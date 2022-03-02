import sys
sys.path.append("../../")
import json, config
import pickle
import util

from connective import Connective
from explicitRelation import ExplicitRelation
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper


def get_ExplicitRelations(relations_path, dest_dir):

    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()
    print("loaded...")

    ExplicitRelation_list = []

    for relation in relations:
        if relation["Type"] != "Explicit":
            continue

        # 去掉6种关系
        Sense = [sense for sense in relation["Sense"] if sense in config.Sense_To_Label.keys()]
        if Sense == []:
            continue

        # connective 不跨句子
        conn_sent_indices = [item[-2] for item in relation["Connective"]["TokenList"]]
        if len(set(conn_sent_indices)) != 1:
            continue

        # connective 的 DocID, sent_index, conn_indices
        ID = relation["ID"]
        DocID = relation["DocID"]
        sent_index = conn_sent_indices[0]

        conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
        #需要将获取语篇连接词的头
        raw_connective = relation["Connective"]["RawText"]
        chm = ConnHeadMapper()
        conn_head, indices = chm.map_raw_connective(raw_connective)
        conn_head_indices = [conn_token_indices[index] for index in indices]
        connective = Connective(DocID, sent_index, conn_head_indices,conn_head)

        Arg1_TokenList = relation["Arg1"]["TokenList"]
        Arg2_TokenList = relation["Arg2"]["TokenList"]

        # Sense Label, 对于有多种sense的选择一个
        SenseLabel = config.Sense_To_Label[Sense[0]]

        explicitRelation = ExplicitRelation(connective)
        explicitRelation.ID = ID
        explicitRelation.Arg1_TokenList = Arg1_TokenList
        explicitRelation.Arg2_TokenList = Arg2_TokenList
        explicitRelation.Sense = Sense
        explicitRelation.SenseLabel = SenseLabel
        ExplicitRelation_list.append(explicitRelation)

    print("Explicit Relation: %d" % len(ExplicitRelation_list))

    # to file
    pickle.dump(ExplicitRelation_list, open(dest_dir + "/explicitRelations.pkl", "wb" ))


if __name__ == "__main__":

    get_ExplicitRelations(config.TRAIN_PATH + "relations.json", config.DATA_PATH + "explicitRelations/train")
    get_ExplicitRelations(config.DEV_PATH + "relations.json", config.DATA_PATH + "explicitRelations/dev")

