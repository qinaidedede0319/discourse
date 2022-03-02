import json

import config
import util
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper


def get_Arg1_acc(parse_dict, relations, dev_feature_path, dev_classifier_out_path):

    gold_PS_relations = get_gold_PS_relations(relations)

    dict_relationID_to_gold_relation = {}
    for relation in gold_PS_relations:
        dict_relationID_to_gold_relation[relation["ID"]] = relation

    dev_feat_file = open(dev_feature_path)
    predicted_list = util.get_mallet_predicted_list(dev_classifier_out_path)
    feature_list = [line.strip() for line in dev_feat_file]

    # relation_dict[relationID] = {(['1', '2'],'1')....}
    dict_relationID_to_predicted_clause_indices = {}
    for feature_line, predicted in zip(feature_list, predicted_list):
        comment = feature_line.split(" # ")[1].strip()

        relationID = int(comment.split("|")[0].strip())
        DocID = comment.split("|")[1].strip()
        clause_sent_index = int(comment.split("|")[2].strip())
        clause_indices = map(int, comment.split("|")[3].strip().split(" "))

        if relationID not in dict_relationID_to_predicted_clause_indices:
            dict_relationID_to_predicted_clause_indices[relationID] = []
        dict_relationID_to_predicted_clause_indices[relationID].append((DocID, clause_sent_index, clause_indices, predicted))

    dict_relationID_to_predicted_Arg1 = {}
    #对每一个relation的arg1,arg2进行合并
    for relationID in dict_relationID_to_predicted_clause_indices:
        DocID = None
        sent_index = None

        Arg_list = []
        predicted_clause_indices = dict_relationID_to_predicted_clause_indices[relationID]
        for _DocID, clause_sent_index, clause_indices, predicted in predicted_clause_indices:# 合并是请补上标点符号，亲！
            DocID = _DocID
            sent_index = clause_sent_index
            if predicted == "1":
                Arg_list.extend(clause_indices)

        Arg_list = sorted(Arg_list)

        Arg_list = merge_for_PS_Arg1(parse_dict, DocID, sent_index, Arg_list)

        dict_relationID_to_predicted_Arg1[relationID] = Arg_list


    # let's evaluate
    #对同一个句子的arg1，arg2 进行精确匹配，评估！
    total = len(dict_relationID_to_gold_relation)
    Arg1_right_relationIDs = set()
    Arg1_right_count = 0
    for relationID in dict_relationID_to_gold_relation:

        if relationID not in dict_relationID_to_gold_relation:
            continue

        gold_relation = dict_relationID_to_gold_relation[relationID]
        gold_Arg1_indices = [word_index for _, _, _, sent_index, word_index in gold_relation["Arg1"]["TokenList"]]

        pred_Arg1_indices = dict_relationID_to_predicted_Arg1[relationID]

        if gold_Arg1_indices == pred_Arg1_indices:
            Arg1_right_count += 1
            Arg1_right_relationIDs.add(relationID)
        else:
            pass

            DocID = gold_relation["DocID"]
            sent_index = gold_relation["Arg1"]["TokenList"][0][-2]

            sent = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
            conn_name = gold_relation["Connective"]["RawText"]

            gold_words = [parse_dict[DocID]["sentences"][sent_index]["words"][index][0] for index in gold_Arg1_indices]
            pred_words = [parse_dict[DocID]["sentences"][sent_index]["words"][index][0] for index in pred_Arg1_indices]
            print("==" * 40)
            print(DocID, sent_index)
            print("Sent: %s" % (" ".join(sent)))
            print("Conn: %s" % (conn_name))
            print("Gold: %s" % (" ".join(gold_words)))
            print("Pred: %s" % (" ".join(pred_words)))

    acc = Arg1_right_count / total * 100
    print("Arg1 accuracy: %.2f%%" % (acc))

    return acc, Arg1_right_relationIDs, dict_relationID_to_gold_relation



#[1,2,4,5,6,7]
def merge_for_PS_Arg1(parse_dict, DocID, sent_index, Arg_list):
    punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~--""" + "``" + "''" + "-LCB--LRB-" + "-RRB--RCB-"
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


def get_gold_PS_relations(relations):


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

            # # PS
            # if Arg2_sent_index == conn_sent_index and Arg1_sent_index < conn_sent_index:
            #     PS_count += 1
            #     PS_relations.append(relation)

            # IPS
            if Arg2_sent_index == conn_sent_index and Arg1_sent_index == conn_sent_index - 1:
                PS_count += 1
                PS_relations.append(relation)


    print("PS/Total: %d/%d=%.4f" % (PS_count, explicit_total, PS_count/explicit_total))

    return PS_relations



if __name__ == "__main__":
    pass
    # get_both_match_acc()