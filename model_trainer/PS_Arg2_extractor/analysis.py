import json
from collections import Counter

import config
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper


def ps_analysis(relations_path, parse_dict_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    parse_file = open(parse_dict_path)
    parse_dict = json.load(parse_file)
    parse_file.close()

    explicit_total = 0

    cross_sentence_conn_counter = 0
    arg_sent_length_counter = Counter()


    #
    PS_count = 0
    PS_Arg1_distance_counter = Counter()


    for relation in relations:
        if relation["Type"] =="Explicit":
            explicit_total += 1

            conn_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Connective"]["TokenList"]]
            if len(set(conn_sent_indices)) > 1:
                cross_sentence_conn_counter += 1

            Arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
            Arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

            arg_sent_length_counter[len(set(Arg1_sent_indices))] += 1
            arg_sent_length_counter[len(set(Arg2_sent_indices))] += 1

            if len(set(Arg1_sent_indices)) == 1 and len(set(Arg2_sent_indices)) == 1:
                pass
            else:
                continue

            # 只考虑 Arg1，Arg2 均为单个句子的情况

            Arg1_sent_index, Arg2_sent_index = Arg1_sent_indices[0], Arg2_sent_indices[0]
            conn_sent_index = conn_sent_indices[0]

            # PS
            if Arg2_sent_index == conn_sent_index and Arg1_sent_index < conn_sent_index:
                PS_count += 1
                PS_Arg1_distance_counter[conn_sent_index - Arg1_sent_index] += 1

                # Arg2
                DocID = relation["DocID"]
                sent_index = conn_sent_index

                conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
                #需要将获取语篇连接词的头
                raw_connective = relation["Connective"]["RawText"]
                chm = ConnHeadMapper()
                conn_head, indices = chm.map_raw_connective(raw_connective)
                conn_head_indices = [conn_token_indices[index] for index in indices]

                words = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
                conn = [parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0] for word_index in conn_head_indices]
                Arg1_words = [parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0] \
                              for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
                Arg2_words = [parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0] \
                              for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

                print("==" * 40)
                print(DocID, sent_index)
                print("Sent:", " ".join(words))
                print("Conn:"," ".join(conn))
                print("Arg2:"," ".join(Arg2_words))


    print("PS/Total: %d/%d=%.4f" % (PS_count, explicit_total, PS_count/explicit_total))
    print("PS_Arg1_distance_counter")
    for PS_Arg1_distance, freq in PS_Arg1_distance_counter.most_common(3):
        print("%d: %d" % (PS_Arg1_distance, freq))


# quotation 分析
#对于-LCB--RCB- 即{}, -LRB- -RRB- 即()
def quotation_analysis(relations_path, parse_dict_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    parse_file = open(parse_dict_path)
    parse_dict = json.load(parse_file)
    parse_file.close()

    quotation = {"-LCB-", "-RCB-", "-LRB-", "-RRB-"}

    for relation in relations:
        DocID = relation["DocID"]

        Arg1_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
        Arg2_sent_indices = [sent_index for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

        if len(set(Arg1_sent_indices)) == 1 and len(set(Arg2_sent_indices)) == 1:
            pass
        else:
            continue

        Arg1_sent_index = Arg1_sent_indices[0]
        Arg2_sent_index = Arg2_sent_indices[0]

        Arg1_sent = [word[0] for word in parse_dict[DocID]["sentences"][Arg1_sent_index]["words"]]
        Arg2_sent = [word[0] for word in parse_dict[DocID]["sentences"][Arg2_sent_index]["words"]]

        Arg1_gold_tokens = [parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0] \
                            for _, _, _, sent_index, word_index in relation["Arg1"]["TokenList"]]
        Arg2_gold_tokens = [parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0] \
                            for _, _, _, sent_index, word_index in relation["Arg2"]["TokenList"]]

        if set(Arg1_sent) & quotation != set([]):
            print("==" * 40)
            print(DocID, Arg1_sent_index, "Arg1")
            print(" ".join(Arg1_sent))
            print(" ".join(Arg1_gold_tokens))

        if set(Arg2_sent) & quotation != set([]):
            print("==" * 40)
            print(DocID, Arg2_sent_index, "Arg2")
            print(" ".join(Arg2_sent))
            print(" ".join(Arg2_gold_tokens))


if __name__ == "__main__":
    quotation_analysis(config.TRAIN_PATH + "/relations.json", config.TRAIN_PATH + "/parses.json")