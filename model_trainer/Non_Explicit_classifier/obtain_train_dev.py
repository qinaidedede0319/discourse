import sys
sys.path.append("../../")
import json, config
import pickle
from nonExplicitRelation import NonExplicitRelation

def get_NonExplicitRelations(relations_path, dest_dir):

    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()
    print("loaded...")

    nonExplicitRelation_list = []

    for relation in relations:
        if relation["Type"] == "Explicit":
            continue

        # 去掉6种关系
        Sense = [sense for sense in relation["Sense"] if sense in config.Sense_To_Label.keys()]
        if Sense == []:
            continue

        ID = relation["ID"]
        DocID = relation["DocID"]

        Arg1_TokenList = relation["Arg1"]["TokenList"]
        Arg2_TokenList = relation["Arg2"]["TokenList"]

        # Sense Label, 对于有多种sense的选择一个
        SenseLabel = config.Sense_To_Label[Sense[0]]

        nonExplicitRelation = NonExplicitRelation()
        nonExplicitRelation.ID = ID
        nonExplicitRelation.DocID = DocID
        nonExplicitRelation.Arg1_TokenList = Arg1_TokenList
        nonExplicitRelation.Arg2_TokenList = Arg2_TokenList
        nonExplicitRelation.Sense = Sense
        nonExplicitRelation.SenseLabel = SenseLabel
        nonExplicitRelation_list.append(nonExplicitRelation)

    print("non-Explicit Relation: %d" % len(nonExplicitRelation_list))

    # to file
    pickle.dump(nonExplicitRelation_list, open(dest_dir + "/nonExplicitRelations.pkl", "wb" ))


if __name__ == "__main__":

    get_NonExplicitRelations(config.TRAIN_PATH + "relations.json", config.DATA_PATH + "nonExplicitRelations/train")
    get_NonExplicitRelations(config.DEV_PATH + "relations.json", config.DATA_PATH + "nonExplicitRelations/dev")

