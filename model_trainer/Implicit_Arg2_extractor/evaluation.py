import json

import config
import util
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper
from model_trainer.Implicit_Arg1_extractor.evaluation import merge_Arg


def get_Arg2_acc(parse_dict, relations, dev_feature_path, dev_classifier_out_path):

    gold_implicit_relations = get_gold_implicit_relations(relations)

    dict_relationID_to_gold_relation = {}
    for relation in gold_implicit_relations:
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

    dict_relationID_to_predicted_Arg2 = {}
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

        Arg_list = merge_Arg(parse_dict, DocID, sent_index, Arg_list)

        dict_relationID_to_predicted_Arg2[relationID] = Arg_list


    # let's evaluate
    #对同一个句子的arg1，arg2 进行精确匹配，评估！
    total = len(dict_relationID_to_gold_relation)
    Arg2_right_relationIDs = set()
    Arg2_right_count = 0
    for relationID in dict_relationID_to_gold_relation:

        if relationID not in dict_relationID_to_gold_relation:
            continue

        gold_relation = dict_relationID_to_gold_relation[relationID]
        gold_Arg2_indices = [word_index for _, _, _, sent_index, word_index in gold_relation["Arg2"]["TokenList"]]

        if relationID in dict_relationID_to_predicted_Arg2:
            pred_Arg2_indices = dict_relationID_to_predicted_Arg2[relationID]

            if gold_Arg2_indices == pred_Arg2_indices:
                Arg2_right_count += 1
                Arg2_right_relationIDs.add(relationID)
            else:
                pass

                DocID = gold_relation["DocID"]
                sent_index = gold_relation["Arg2"]["TokenList"][0][-2]

                sent = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
                conn_name = gold_relation["Connective"]["RawText"]

                gold_words = [parse_dict[DocID]["sentences"][sent_index]["words"][index][0] for index in gold_Arg2_indices]
                pred_words = [parse_dict[DocID]["sentences"][sent_index]["words"][index][0] for index in pred_Arg2_indices]
                print("==" * 40)
                print(DocID, sent_index)
                print("Sent: %s" % (" ".join(sent)))
                print("Conn: %s" % (conn_name))
                print("Gold: %s" % (" ".join(gold_words)))
                print("Pred: %s" % (" ".join(pred_words)))

    acc = Arg2_right_count / total * 100
    print("Arg2 accuracy: %.2f%%" % (acc))

    return acc, Arg2_right_relationIDs, dict_relationID_to_gold_relation





def get_gold_implicit_relations(relations):

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



if __name__ == "__main__":
    pass
    # get_both_match_acc()