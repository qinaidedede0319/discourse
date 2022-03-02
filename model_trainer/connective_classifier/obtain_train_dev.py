import sys

sys.path.append("../../")
import pickle
import json
# from util import *
import util
import config
from dict_loader.connective_dict_loader import Connectives_dict_loader
from model_trainer.connective_classifier.conn_head_mapper import ConnHeadMapper
from connective import Connective
from parser_util import get_conn_name

''' 识别sentence中的连接词, 返回识别出来的连接词的indices # [([2,6], 'for instance'), ....] '''
def check_connectives(sent_tokens):
    sent_tokens = [word.lower() for word in sent_tokens ]

    conn_indices = []

    visited = [False] * len(sent_tokens)

    sortedConn = Connectives_dict_loader().sorted_conns_list
    for conn in sortedConn:
        #判断连接词是否在句子中出现
        if '..' in conn:#对于这种类型的在sentence中只识别一次
            c1, c2 = conn.split('..')

            c1_indices = util.getSpanIndecesInSent(c1.split(), sent_tokens)#[(4,), (7,)]
            c2_indices = util.getSpanIndecesInSent(c2.split(), sent_tokens)#[[6], [11]]

            # if len(c1_indices)>0:
            #     print(c1_indices) 

            # if : c1_list = [(1,), (2,), (4,)]
            # then: c2_list = [(3,), (5,)]
            # return: if..then: [(2, 3), (4, 5)], [(1,)]
            parallel_connective, _ = get_parallel_connective(c1_indices, c2_indices)

            conn_indices += parallel_connective

            # for item in parallel_connective:
            #     for x in item:
            #         visited[x] = True

        else:
            c_indices = util.getSpanIndecesInSent(conn.split(), sent_tokens)#[(2,6), (1,3),...]

            for item in c_indices:
                flag = 1
                for x in item:
                   if visited[x] == True:
                       flag = 0

                if flag == 1:
                    conn_indices.append(item)
                    for x in item:
                        visited[x] = True


    # [(3, 4), (8, 9), (5,), (6,), (7,), (1,)]
    # [((1,), 'if'), ((3, 4), 'if then'), ((5,), 'and'), ((6,), 'and'), ((7,), 'and'), ((8, 9), 'as if')]
    conn_indices = sorted(conn_indices, key=lambda x: x[0])
    new_conn_indices = []
    for item in conn_indices:
        name = " ".join([sent_tokens[i] for i in item])
        new_conn_indices.append((list(item), name))

    return new_conn_indices


#
# if : c1_list = [[1], [2], [4]]
# then: c2_list = [[3], [5]]
# return: if..then: [(2, 3), (4, 5)], [(1,)]
def get_parallel_connective(c1_list, c2_list):
    c1_list = sorted(c1_list, key=lambda x: x[0])
    c2_list = sorted(c2_list, key=lambda x: x[0])

    c1_visited = [False] * len(c1_list)

    parallel_connective = []
    non_parallel_connective = []

    for c2_index in range(len(c2_list)):

        distances = [c2_list[c2_index][0] - c1_list[index][-1] for index in range(len(c1_list))]
        min_index = -1
        min_value = 1000000000
        for c1_index, distance in enumerate(distances):
            if c1_visited[c1_index] == True or distance <= 0:
                continue
            if distance < min_value:
                min_value = distance
                min_index = c1_index

        # 没有找到
        if min_index == - 1:
            non_parallel_connective.append(c2_list[c2_index])
        else:
            parallel_connective.append(tuple(c1_list[min_index] + c2_list[c2_index]))
            c1_visited[min_index] = True

    for c1, visited in zip(c1_list, c1_visited):
        if visited is False:
            non_parallel_connective.append(tuple(c1))


    return parallel_connective, non_parallel_connective




#从pdtb数据集中获取语篇连接词
# 构成字典：dict[("DocID", sent_index)] = [[0], [1, 2]]
def get_disc_conns_and_non_disc_for_train(relations_path, parse_path, dest_dir):

    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    parse_file = open(parse_path)
    parse_dict = json.load(parse_file)
    parse_file.close()

    print("loaded...")


    # discourse connective
    disc_conns_dict = {}
    for relation in relations:
        if relation["Type"] == "Explicit":
            DocID = relation["DocID"]
            sent_index = relation["Connective"]["TokenList"][0][3]
            conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
            #需要将获取语篇连接词的头
            raw_connective = relation["Connective"]["RawText"]
            chm = ConnHeadMapper()
            conn_head, indices = chm.map_raw_connective(raw_connective)
            conn_head_indices = [conn_token_indices[index] for index in indices]

            if (DocID, sent_index) not in disc_conns_dict:
                disc_conns_dict[(DocID, sent_index)] = []
            disc_conns_dict[(DocID, sent_index)].append(conn_head_indices)


    # non-discourse connective
    non_disc_conns_dict = {}

    found_connective_count = 0
    found_discourse_connective_count = 0

    #1. 识别每一句子中的连接词
    for DocID in parse_dict:
        for sent_index in range(len(parse_dict[DocID]["sentences"])):
            sent_tokens = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
            #在sentence中标注连接词，[([2,6], 'for instance'), ....]
            for token_indices, conn_name in check_connectives(sent_tokens):
                found_connective_count += 1

                #2. 判断该连接词是否是disc_conn,
                flag = 1
                disc_conns = [[]]
                if (DocID, sent_index) in disc_conns_dict:
                    disc_conns = disc_conns_dict[(DocID, sent_index)]
                for disc_conn in disc_conns:
                    # # 与其中一项有交集, 就认为是语篇连接词
                    # if set(token_indices) & set(item) != set([]):
                    #     flag = 0
                    #     break
                    # 与其中一项相等, 就认为是语篇连接词
                    if set(token_indices) == set(disc_conn):
                        flag = 0
                        found_discourse_connective_count += 1
                        break

                        # 对于 Train 集合, 那些与 discourse 有交集的, 不一定是负样本
                    if set(token_indices) & set(disc_conn) != set([]) and set(token_indices) != set(disc_conn):
                        flag = -1

                if flag == 1:
                    if (DocID, sent_index) not in non_disc_conns_dict:
                        non_disc_conns_dict[(DocID, sent_index)] = []
                    non_disc_conns_dict[(DocID, sent_index)].append(token_indices)


    disc_conns_count = 0
    non_disc_conns_count = 0
    connectives = []
    for (DocID, sent_index) in disc_conns_dict:
        disc_conns = disc_conns_dict[(DocID, sent_index)]
        for conn_indices in disc_conns:
            conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)
            connective = Connective(DocID, sent_index, conn_indices, conn_name)
            connective.label = 1
            connectives.append(connective)
            disc_conns_count += 1

    for (DocID, sent_index) in non_disc_conns_dict:
        non_disc_conns = non_disc_conns_dict[(DocID, sent_index)]
        for conn_indices in non_disc_conns:
            conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)
            connective = Connective(DocID, sent_index, conn_indices, conn_name)
            connective.label = 0
            connectives.append(connective)
            non_disc_conns_count += 1

    print("found_connective_count: %d" % found_connective_count)
    print("found_discourse_connective_count: %d" % found_discourse_connective_count)

    print("discourse connective: %d" % (disc_conns_count))
    print("non-discourse connective: %d" % (non_disc_conns_count))

    # to file
    pickle.dump(connectives, open(dest_dir + "/disc_and_non_disc_conn.pkl", "wb" ))



#从pdtb数据集中获取语篇连接词
# 构成字典：dict[("DocID", sent_index)] = [[0], [1, 2]]
def get_disc_conns_and_non_disc_for_dev(relations_path, parse_path, dest_dir):

    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    parse_file = open(parse_path)
    parse_dict = json.load(parse_file)
    parse_file.close()

    print("loaded...")


    # discourse connective
    disc_conns_dict = {}
    for relation in relations:
        if relation["Type"] == "Explicit":
            DocID = relation["DocID"]
            sent_index = relation["Connective"]["TokenList"][0][3]
            conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
            #需要将获取语篇连接词的头
            raw_connective = relation["Connective"]["RawText"]
            chm = ConnHeadMapper()
            conn_head, indices = chm.map_raw_connective(raw_connective)
            conn_head_indices = [conn_token_indices[index] for index in indices]

            if (DocID, sent_index) not in disc_conns_dict:
                disc_conns_dict[(DocID, sent_index)] = []
            disc_conns_dict[(DocID, sent_index)].append(conn_head_indices)


    # non-discourse connective
    non_disc_conns_dict = {}

    found_connective_count = 0
    found_discourse_connective_count = 0

    #1. 识别每一句子中的连接词
    for DocID in parse_dict:
        for sent_index in range(len(parse_dict[DocID]["sentences"])):
            sent_tokens = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
            #在sentence中标注连接词，[([2,6], 'for instance'), ....]
            for token_indices, conn_name in check_connectives(sent_tokens):
                found_connective_count += 1
                #2. 判断该连接词是否是disc_conn,
                flag = 1
                disc_conns = [[]]
                if (DocID, sent_index) in disc_conns_dict:
                    disc_conns = disc_conns_dict[(DocID, sent_index)]
                for item in disc_conns:
                    # # 与其中一项有交集, 就认为是语篇连接词
                    # if set(token_indices) & set(item) != set([]):
                    #     flag = 0
                    #     break
                    # 与其中一项相等, 就认为是语篇连接词
                    if set(token_indices) == set(item):
                        flag = 0
                        found_discourse_connective_count += 1
                        break
                if flag == 1:
                    if (DocID, sent_index) not in non_disc_conns_dict:
                        non_disc_conns_dict[(DocID, sent_index)] = []
                    non_disc_conns_dict[(DocID, sent_index)].append(token_indices)


    disc_conns_count = 0
    non_disc_conns_count = 0
    connectives = []
    for (DocID, sent_index) in disc_conns_dict:
        disc_conns = disc_conns_dict[(DocID, sent_index)]
        for conn_indices in disc_conns:
            conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)
            connective = Connective(DocID, sent_index, conn_indices, conn_name)
            connective.label = 1
            connectives.append(connective)
            disc_conns_count += 1

    for (DocID, sent_index) in non_disc_conns_dict:
        non_disc_conns = non_disc_conns_dict[(DocID, sent_index)]
        for conn_indices in non_disc_conns:
            conn_name = get_conn_name(parse_dict, DocID, sent_index, conn_indices)
            connective = Connective(DocID, sent_index, conn_indices, conn_name)
            connective.label = 0
            connectives.append(connective)
            non_disc_conns_count += 1

    print("found_connective_count: %d" % found_connective_count)
    print("found_discourse_connective_count: %d" % found_discourse_connective_count)

    print("discourse connective: %d" % (disc_conns_count))
    print("non-discourse connective: %d" % (non_disc_conns_count))

    # to file
    pickle.dump(connectives, open(dest_dir + "/disc_and_non_disc_conn.pkl", "wb" ))


def test_cover(relations_path, parse_path):
    relations_file = open(relations_path)
    relations = [json.loads(x) for x in relations_file]
    relations_file.close()

    parse_file = open(parse_path)
    parse_dict = json.load(parse_file)
    parse_file.close()

    print("loaded...")

    # discourse connective
    disc_conns_dict = {}
    for relation in relations:
        if relation["Type"] == "Explicit":

            # 只使用存在于单个句子的连接词
            if len(set([x[-2] for x in relation["Connective"]["TokenList"]])) != 1:
                continue

            DocID = relation["DocID"]
            sent_index = relation["Connective"]["TokenList"][0][3]
            conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
            # 需要将获取语篇连接词的头
            raw_connective = relation["Connective"]["RawText"]
            chm = ConnHeadMapper()
            conn_head, indices = chm.map_raw_connective(raw_connective)
            conn_head_indices = [conn_token_indices[index] for index in indices]

            if (DocID, sent_index) not in disc_conns_dict:
                disc_conns_dict[(DocID, sent_index)] = []
            disc_conns_dict[(DocID, sent_index)].append(conn_head_indices)


    found_conns_dict = {}
    for DocID in parse_dict:
        for sent_index in range(len(parse_dict[DocID]["sentences"])):
            sent_tokens = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]
            # 在sentence中标注连接词，[([2,6], 'for instance'), ....]
            for token_indices, conn_name in check_connectives(sent_tokens):
                if (DocID, sent_index) not in found_conns_dict:
                    found_conns_dict[(DocID, sent_index)] = []
                found_conns_dict[(DocID, sent_index)].append(token_indices)



    index= 0
    for (DocID, sent_index) in disc_conns_dict:
        for conn_indices in disc_conns_dict[(DocID, sent_index)]:

            if (DocID, sent_index) not in found_conns_dict:
                print(DocID, sent_index)
                continue
            flag = 0
            for found_conn_indices in found_conns_dict[(DocID, sent_index)]:
                if found_conn_indices == conn_indices:
                    flag = 1
                    break
            if flag == 0:
                index += 1

                words = [word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]]

                print(index)
                print(" ".join(words))
                print(DocID, sent_index, conn_indices, " ".join( parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0] for word_index in conn_indices))
                print("found", found_conns_dict[(DocID, sent_index)])
                print("==" * 40)


def print_instances_by_connective(conn_rawText):
    fin = open(config.TRAIN_PATH + "relations.json")
    train_relations = [json.loads(x) for x in fin]
    fin.close()

    parse_file = open(config.TRAIN_PATH + "pdtb-parses.json")
    parse_dict = json.load(parse_file)

    i = 0

    for relation in train_relations:
        if relation["Type"] != "Explicit":
            continue

        # connective  在单个句子中
        if len(set([x[3] for x in relation["Connective"]["TokenList"]])) != 1:
            continue



        #
        DocID = relation["DocID"]
        sent_index = relation["Connective"]["TokenList"][0][3]
        conn_indices = [item[-1] for item in relation["Connective"]["TokenList"]]
        # 需要将获取语篇连接词的头
        raw_connective = relation["Connective"]["RawText"]
        chm = ConnHeadMapper()
        conn_head, indices = chm.map_raw_connective(raw_connective)
        conn_head_indices = [conn_indices[index] for index in indices]

        conn_name = " ".join([parse_dict[DocID]["sentences"][sent_index]["words"][index][0].lower() for index in conn_head_indices])

        if conn_name != conn_rawText:
            continue


        sent = " ".join([word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]])

        i += 1
        print("==" * 40)
        print(i)
        print(DocID, sent_index, conn_head_indices)
        print(conn_rawText)
        print(sent)


def print_instances_by_conn_name(conn_name, to_file=None):

    positive_instances = []
    negative_instances = []

    with \
            open(config.TRAIN_PATH + "pdtb-parses.json") as train_parse_file, \
            open(config.DATA_PATH + "/disc_vs_non_disc_conn/train/disc_and_non_disc_conn.pkl", "rb") as train_pkl_file:

        parse_dict = json.load(train_parse_file)
        connectives = pickle.load(train_pkl_file)

        for connective in connectives:
            label = connective.label

            DocID = connective.DocID
            sent_index = connective.sent_index
            conn_indices = connective.token_indices

            this_conn_name = " ".join([parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0].lower()
                         for word_index in conn_indices])

            if this_conn_name == conn_name:
                sent = " ".join([word[0] for word in parse_dict[DocID]["sentences"][sent_index]["words"]])

                instance = "==" * 40 + "\n"
                instance += "Label: %d\n" % label
                instance += sent + "\n"
                instance += "%s\t%s\t%s\t%s" % (DocID, str(sent_index), str(conn_indices), conn_name)

                if label == 1:
                    positive_instances.append(instance)
                if label == 0:
                    negative_instances.append(instance)

    print("\n".join(positive_instances) + "\n")
    print("\n".join(negative_instances))

    if to_file:
        fout = open(to_file, "w")
        fout.write("\n".join(positive_instances) + "\n")
        fout.write("\n".join(negative_instances))







if __name__ == "__main__":

    s = "But when Betsy Engelken wrote him , saying she could stop near his New Jersey home , it seemed different"
    print(check_connectives(s.split(" ")))

    print(get_parallel_connective([[1], [2], [4]], [[3], [5]]))

    print_instances_by_connective("if then")


    test_cover(config.TRAIN_PATH + "relations.json", config.TRAIN_PATH + "pdtb-parses.json")
    
    test_cover(config.DEV_PATH + "relations.json", config.DEV_PATH + "pdtb-parses.json")

    relations_path = config.TRAIN_PATH + "relations.json"
    parse_path = config.TRAIN_PATH + "pdtb-parses.json"
    get_disc_conns_and_non_disc_for_train(relations_path, parse_path, config.DATA_PATH + "disc_vs_non_disc_conn/train")
    
    relations_path = config.DEV_PATH + "relations.json"
    parse_path = config.DEV_PATH + "pdtb-parses.json"
    get_disc_conns_and_non_disc_for_dev(relations_path, parse_path, config.DATA_PATH + "disc_vs_non_disc_conn/dev")


    print_instances_by_conn_name("and", config.CWD+"tmp/conn_instances.txt")