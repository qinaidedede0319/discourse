import json

import util
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper


def get_Arg_acc(parse_dict, relations, dev_feature_path, dev_classifier_out_path):

    gold_SS_relations = get_gold_Explicit_SS_relations(relations)

    dict_relationID_to_gold_relation = {}
    for relation in gold_SS_relations:
        dict_relationID_to_gold_relation[relation["ID"]] = relation


    dev_feat_file = open(dev_feature_path)
    predicted_list = util.get_mallet_predicted_list(dev_classifier_out_path)
    feature_list = [line.strip() for line in dev_feat_file]

    # relation_dict[relationID] = {(['1', '2'],'Arg1')....}
    dict_relationID_to_predicted_constituent_indices = {}
    for feature_line, predicted in zip(feature_list, predicted_list):
        comment = feature_line.split(" # ")[1].strip()
        relationID = int(comment.split("|")[0].strip())
        constituent_indices = map(int, comment.split("|")[-1].strip().split(" "))
        if relationID not in dict_relationID_to_predicted_constituent_indices:
            dict_relationID_to_predicted_constituent_indices[relationID] = [(constituent_indices, predicted)]
        else:
            dict_relationID_to_predicted_constituent_indices[relationID].append((constituent_indices, predicted))

    dict_relationID_to_predicted_Arg1 = {}
    dict_relationID_to_predicted_Arg2 = {}

    #对每一个relation的arg1,arg2进行合并
    for relationID in dict_relationID_to_predicted_constituent_indices:
        gold_relation = dict_relationID_to_gold_relation[relationID]

        DocID = gold_relation["DocID"]
        sent_index = gold_relation["Connective"]["TokenList"][0][-2]

        Arg1_list = []
        Arg2_list = []
        predicted_constituents = dict_relationID_to_predicted_constituent_indices[relationID]
        for constituent_indices, pred in predicted_constituents:# 合并是请补上标点符号，亲！
            if pred == "1":
                Arg1_list.extend(constituent_indices)
            elif pred == "2":
                Arg2_list.extend(constituent_indices)

        Arg1_list = sorted(set(Arg1_list))
        Arg2_list = sorted(set(Arg2_list))

        Arg1_list = merge_NT_Arg(parse_dict, DocID, sent_index, Arg1_list)
        Arg2_list = merge_NT_Arg(parse_dict, DocID, sent_index, Arg2_list)

        dict_relationID_to_predicted_Arg1[relationID] = Arg1_list
        dict_relationID_to_predicted_Arg2[relationID] = Arg2_list


    # let's evaluate
    #对同一个句子的arg1，arg2 进行精确匹配，评估！
    total = len(dict_relationID_to_gold_relation)
    Arg1_right_relationIDs = set()
    Arg1_right_count = 0
    Arg2_right_relationIDs = set()
    Arg2_right_count = 0
    for relationID in dict_relationID_to_gold_relation:

        if relationID not in dict_relationID_to_gold_relation:
            continue

        gold_relation = dict_relationID_to_gold_relation[relationID]

        gold_Arg1_indices = [word_index for _, _, _, sent_index, word_index in gold_relation["Arg1"]["TokenList"]]
        pred_Arg1_indices = dict_relationID_to_predicted_Arg1[relationID]

        gold_Arg2_indices = [word_index for _, _, _, sent_index, word_index in gold_relation["Arg2"]["TokenList"]]
        pred_Arg2_indices = dict_relationID_to_predicted_Arg2[relationID]

        if gold_Arg1_indices == pred_Arg1_indices:
            Arg1_right_count += 1
            Arg1_right_relationIDs.add(relationID)

        if gold_Arg2_indices == pred_Arg2_indices:
            DocID = gold_relation["DocID"]
            sent_index = gold_relation["Connective"]["TokenList"][0][-2]
            conn_indices = [word_index for _, _, _, _, word_index in gold_relation["Connective"]["TokenList"]]
            print(DocID, sent_index, conn_indices)

            Arg2_right_count += 1
            Arg2_right_relationIDs.add(relationID)

    acc = Arg1_right_count / total * 100
    print("Arg1 accuracy: %.2f%%" % (acc))

    acc = Arg2_right_count / total * 100
    print("Arg2 accuracy: %.2f%%" % (acc))

    return acc, Arg1_right_relationIDs,Arg2_right_relationIDs, dict_relationID_to_gold_relation



#[1,2,4,5,6,7]
def merge_NT_Arg(parse_dict, DocID, sent_index, Arg_list):
    punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~""" + "``" + "''"
    if len(Arg_list) <= 1:
        return Arg_list
    temp = []
    #扫描丢失的部分，是否是标点符号，是则补上
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
                if flag == 1:#都是标点，补齐
                    temp += range(item + 1, next_item)
    temp.append(Arg_list[-1])

    #两侧的逗号要删除
    Arg = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in temp]
    #去两边的标点
    Arg = util.list_strip_punctuation(Arg)

    Arg = [item[0] for item in Arg]

    return Arg


def get_gold_Explicit_SS_relations(relations):


    gold_Explicit_SS_relations = []

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

                gold_Explicit_SS_relations.append(relation)

    return gold_Explicit_SS_relations



