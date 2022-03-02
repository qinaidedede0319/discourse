import sys
sys.path.append("../../")
from operator import itemgetter
from model_trainer.mallet_classifier import *

from feature import Feature
from model_trainer.connective_classifier.trainer import do_evaluation, write_error_cases_to_file
import json, math
import os
import pickle
import config
from model_trainer.connective_classifier.feature_functions import *
from model_trainer.connective_classifier.make_feature_file import Make_feature_file
import util

class Feat_examples:
    def __init__(self, name, dimension, target_list, feat_list, comment_list):
        self.name = name
        self.dimension = dimension
        self.target_list = target_list
        self.feat_list = feat_list
        self.comment_list = comment_list

def generate_feat_file(feature_function_list, dest_dir):

    with \
        open(config.TRAIN_PATH + "/parses_lemma_ner.json") as train_parse_file, \
        open(config.DEV_PATH + "/parses_lemma_ner.json") as dev_parse_file, \
        open(config.DATA_PATH + "/disc_vs_non_disc_conn/train/disc_and_non_disc_conn.pkl", "rb") as train_pkl_file, \
        open(config.DATA_PATH + "/disc_vs_non_disc_conn/dev/disc_and_non_disc_conn.pkl", "rb") as dev_pkl_file:

        train_parse_dict = json.load(train_parse_file)
        dev_parse_dict = json.load(dev_parse_file)
        print("parse dict is loaded...")
        train_connectives = pickle.load(train_pkl_file)
        dev_connectives = pickle.load(dev_pkl_file)
        print("connective is loaded...")


    for i, feature_function in enumerate(feature_function_list):
        train_feature_path = dest_dir + "/train/%s" % (feature_function.__name__)
        dev_feature_path = dest_dir + "/dev/%s" % (feature_function.__name__)

        print("-"*120)
        print("%d: %s" % (i, feature_function.__name__))
        print("-" * 120)

        print("make train feature_file file ...")
        Make_feature_file(train_parse_dict, train_connectives, [feature_function], train_feature_path, add_dimension=True)
        print("make dev feature_file file ...")
        Make_feature_file(dev_parse_dict, dev_connectives, [feature_function], dev_feature_path, add_dimension=True)




def load_feat_examples(dest_dir):
    train_feat_names = util.listdir_no_hidden(dest_dir + "/train")
    dev_feat_names = util.listdir_no_hidden(dest_dir + "/dev")

    dict_train_feat_examples = {}
    for feat_name in train_feat_names:
        train_feat_examples = get_feat_examples(dest_dir + "/train", feat_name)
        dict_train_feat_examples[train_feat_examples.name] = train_feat_examples

    dict_dev_feat_examples = {}
    for feat_name in dev_feat_names:
        dev_feat_examples = get_feat_examples(dest_dir + "/dev", feat_name)
        dict_dev_feat_examples[dev_feat_examples.name] = dev_feat_examples

    assert dict_train_feat_examples.keys() == dict_dev_feat_examples.keys()

    return [dict_train_feat_examples, dict_dev_feat_examples]


# (feat_name, target, comment, [feat, feat, ])
def get_feat_examples(path, feat_name):
    file = open("%s/%s" % (path, feat_name))

    dimension = int(feat_name.split("_")[-1])
    feat_name = "_".join(feat_name.split("_")[:-1])

    feat_list = []
    target_list = []
    comment_list = []

    for line in file:
        line = line.strip()
        comment_list.append(line.split("#")[-1].strip())
        line = line.split("#")[0].strip()
        target_list.append(line.split(" ")[0])
        feat_string = " ".join(line.split(" ")[1:])
        feat = Feature(feat_name, dimension, {})
        feat.feat_string = feat_string

        feat_list.append(feat)

    return Feat_examples(feat_name, dimension, target_list, feat_list, comment_list)

def get_feat_examples_by_feat_name_list(dict_feat_examples, feat_name_list):
    feat_examples_list = []
    for feat_name in sorted(feat_name_list):
        feat_examples_list.append(dict_feat_examples[feat_name])

    target_list = feat_examples_list[0].target_list
    dimension = sum([feat_examples.dimension for feat_examples in feat_examples_list])
    comment_list = feat_examples_list[0].comment_list

    feat_list = []
    feats_list = [feat_examples.feat_list for feat_examples in feat_examples_list]
    for item in zip(*feats_list):
        feat_list.append(util.mergeFeatures(item))

    return Feat_examples("merged_feat", dimension, target_list, feat_list, comment_list)


def make_feature_file_by_feat_examples(feat_examples, to_file):
    target_list = feat_examples.target_list
    feat_list = feat_examples.feat_list
    comment_list = feat_examples.comment_list

    examples = []
    for target, feature, comment in zip(target_list, feat_list, comment_list):
        example = "%s %s # %s" % (target, feature.feat_string, comment)
        examples.append(example)

    fout = open(to_file, "w")
    fout.write("\n".join(examples))
    fout.close()


def do_hill_climbing():
    # feature_file function list
    feature_function_list = [
        # Lin
        # CPOS,
        # prev_C,
        # prevPOS,
        # prevPOS_CPOS,
        # C_next,
        # nextPOS,
        # CPOS_nextPOS,
        # CParent_to_root_path,
        # compressed_cparent_to_root_path,
        # # pitler
        # self_category,
        # parent_category,
        # right_sibling_category,
        # left_sibling_category,
        # is_right_sibling_contains_VP,
        # # conn - syn
        # conn_self_category,
        # conn_parent_category,
        # conn_left_sibling_category,
        # conn_right_sibling_category,
        # # syn - syn
        # self_parent,
        # self_right,
        # self_left,
        # parent_left,
        # parent_right,
        # left_right,
        # # mine
        # conn_name,
        # conn_lower_case,
        # CParent_to_root_path_node_names,
        #
        # conn_connCtx,
        # conn_connLinkedCtx,
        #
        # conn_rightSiblingCtx,
        # conn_rightSiblingLinkedCtx,
        #
        # conn_leftSiblingCtx,
        # conn_leftSiblingLinkedCtx,
        #
        # conn_parent_categoryCtx,
        # conn_parent_categoryLinkedCtx,

        # when_prev_have_DATE_TIME,

        conn_cat,
    ]

    cwd = os.getcwd()
    dest_dir = cwd + "/tmp"
    util.make_dirs([dest_dir, dest_dir + "/train", dest_dir + "/dev"])
    # generate feature_file file in temp dir
    generate_feat_file(feature_function_list, dest_dir)

    # [(feat_name, [feat, feat, ])....]
    dict_train_feat_examples, dict_dev_feat_examples = load_feat_examples(dest_dir)

    ''' classifier '''
    classifier = Classifier(LIB_LINEAR_LR())
    # classifier = Classifier(MaxEnt())

    train_feat_file = dest_dir + "/train_feature.txt"
    dev_feat_file = dest_dir + "/dev_feature.txt"
    model_path = dest_dir + "/train.model"
    dev_result_file = dest_dir + "/dev_result.txt"

    # 所有的feats, ['A', "B]
    all_feats = dict_train_feat_examples.keys()

    num_iter = (len(all_feats) + 1) * len(all_feats) / 2 + 1
    curr_iter = 0

    best_feats = []
    curr_best_score = -1
    curr_best_features = ""

    dict_feat_functions_to_score = {}

    while len(best_feats) != len(all_feats):
        T = list(set(all_feats) - set(best_feats))
        score = [0] * len(T)
        for index, feat_name in enumerate(T):

            curr_iter += 1

            train_feat_names = best_feats + [feat_name]
            dev_feat_names = best_feats + [feat_name]

            train_feat_example = get_feat_examples_by_feat_name_list(dict_train_feat_examples, train_feat_names)
            dev_feat_example = get_feat_examples_by_feat_name_list(dict_dev_feat_examples, dev_feat_names)

            print("make  feature ...")
            print("==" * 40)
            print(" || ".join(train_feat_names))
            print("==" * 40)
            make_feature_file_by_feat_examples(train_feat_example, train_feat_file)
            make_feature_file_by_feat_examples(dev_feat_example, dev_feat_file)

            # 训练
            classifier.train_model(train_feat_file, model_path)
            # 测试
            classifier.test_model(dev_feat_file, model_path, dev_result_file)
            # 结果
            s = do_evaluation(dev_result_file) * 100
            score[index] = s
            if s > curr_best_score:
                curr_best_score = s
                curr_best_features = " ".join(train_feat_names)

            print("-->%d/%d" % (curr_iter, num_iter))
            print("##" * 45)
            print("Current Best : %.2f" % curr_best_score)
            print("Current Best Features: %s" % curr_best_features)
            print("##" * 45)

            # 加入字典
            feat_func_name = " ".join(train_feat_names)
            dict_feat_functions_to_score[feat_func_name] = s

        # 将最好的放入 best_feature_list
        best_index = score.index(max(score))
        best_feats.append(T[best_index])

    # 全部加入的
    curr_iter += 1
    train_feat_names = all_feats
    dev_feat_names = all_feats

    train_feat_example = get_feat_examples_by_feat_name_list(dict_train_feat_examples, train_feat_names)
    dev_feat_example = get_feat_examples_by_feat_name_list(dict_dev_feat_examples, dev_feat_names)

    print("make  feature ...")
    print("==" * 40)
    print(" || ".join(train_feat_names))
    print("==" * 40)
    make_feature_file_by_feat_examples(train_feat_example, train_feat_file)
    make_feature_file_by_feat_examples(dev_feat_example, dev_feat_file)

    # 训练
    classifier.train_model(train_feat_file, model_path)
    # 测试
    classifier.test_model(dev_feat_file, model_path, dev_result_file)
    # 结果
    s = do_evaluation(dev_result_file) * 100

    if s > curr_best_score:
        curr_best_score = s
        curr_best_features = " ".join(train_feat_names)

    print("-->%d/%d" % (curr_iter, num_iter))
    print("##" * 45)
    print("Current Best : %.2f" % curr_best_score)
    print("Current Best Features: %s" % curr_best_features)
    print("##" * 45)

    # 加入字典
    feat_func_name = " ".join(train_feat_names)
    dict_feat_functions_to_score[feat_func_name] = s

    # 将各种特征的组合及对应的score写入文件, 按sore降排
    fout = open(dest_dir + "/liblinear_result.txt", "w")
    # fout = open(dest_dir + "/maxent_result.txt", "w")
    for func_names, score in sorted(dict_feat_functions_to_score.items(), key=itemgetter(1), reverse=True):
        fout.write("%s : %.2f\n" % (func_names, score))
    fout.close()

def train_using_specific_features(feat_names, c=1):

    # cwd = os.getcwd()
    dest_dir = config.CWD + "tmp"


    # [(feat_name, [feat, feat, ])....]
    dict_train_feat_examples, dict_dev_feat_examples = load_feat_examples(dest_dir)


    ''' classifier '''
    # classifier = Classifier(LIB_LINEAR_LR())
    classifier = Mallet_classifier(MaxEnt())

    train_feat_file = dest_dir + "/train_feature.txt"
    dev_feat_file = dest_dir + "/dev_feature.txt"
    model_path = dest_dir + "/train.model"
    dev_result_file = dest_dir + "/dev_result.txt"

    train_feat_names = feat_names
    dev_feat_names = feat_names

    train_feat_example = get_feat_examples_by_feat_name_list(dict_train_feat_examples, train_feat_names)
    dev_feat_example = get_feat_examples_by_feat_name_list(dict_dev_feat_examples, dev_feat_names)

    print("make  feature ...")
    print("==" * 40)
    print(" || ".join(train_feat_names))
    print("==" * 40)
    make_feature_file_by_feat_examples(train_feat_example, train_feat_file)
    make_feature_file_by_feat_examples(dev_feat_example, dev_feat_file)

    #训练
    classifier.train_model(train_feat_file, model_path)
    #测试
    classifier.test_model(dev_feat_file, model_path, dev_result_file)
    #结果
    s = do_evaluation(dev_result_file) * 100

    with \
        open(config.DEV_PATH + "/parses.json") as dev_parse_file:
        dev_parse_dict = json.load(dev_parse_file)

    err_case_path = "tmp/error_cases.txt"
    write_error_cases_to_file(dev_parse_dict, dev_feat_file, dev_result_file, err_case_path)

    print("Acc: %.2f" % s)



def train_using_specific_features_tune_C(feat_names):

    cwd = os.getcwd()
    dest_dir = cwd + "/tmp"


    # [(feat_name, [feat, feat, ])....]
    dict_train_feat_examples, dict_dev_feat_examples = load_feat_examples(dest_dir)


    ''' classifier '''
    classifier = LIB_LINEAR_LR_tune_C()

    train_feat_file = dest_dir + "/train_feature.txt"
    dev_feat_file = dest_dir + "/dev_feature.txt"
    model_path = dest_dir + "/train.model"
    dev_result_file = dest_dir + "/dev_result.txt"

    train_feat_names = feat_names
    dev_feat_names = feat_names

    train_feat_example = get_feat_examples_by_feat_name_list(dict_train_feat_examples, train_feat_names)
    dev_feat_example = get_feat_examples_by_feat_name_list(dict_dev_feat_examples, dev_feat_names)

    print("make  feature ...")
    print("==" * 40)
    print(" || ".join(train_feat_names))
    print("==" * 40)
    make_feature_file_by_feat_examples(train_feat_example, train_feat_file)
    make_feature_file_by_feat_examples(dev_feat_example, dev_feat_file)

    #训练
    classifier.train_model(train_feat_file, model_path)
    #测试
    classifier.test_model(dev_feat_file, model_path, dev_result_file)
    #结果
    s = do_evaluation(dev_result_file) * 100

    with \
        open(config.DEV_PATH + "/parses.json") as dev_parse_file:
        dev_parse_dict = json.load(dev_parse_file)

    err_case_path = "tmp/error_cases.txt"
    write_error_cases_to_file(dev_parse_dict, dev_feat_file, dev_result_file, err_case_path)

    print("Acc: %.2f" % s)

if __name__ == "__main__":
    # do_hill_climbing()

    feat_string = "conn_rightSiblingCtx conn_parent_categoryLinkedCtx conn_rightSiblingLinkedCtx prevPOS_CPOS self_right self_category conn_lower_case conn_cat CPOS left_sibling_category C_next CParent_to_root_path_node_names prev_C conn_parent_category is_right_sibling_contains_VP right_sibling_category CParent_to_root_path"
    train_using_specific_features(feat_string.split(" "))

    # train_using_specific_features_tune_C(feat_string.split(" "))
