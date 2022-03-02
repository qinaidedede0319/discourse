import sys
sys.path.append("../../")
from model_trainer.arg_position_classifier.make_feature_file import Make_feature_file
from model_trainer.mallet_classifier import *

import json, pickle
from model_trainer.arg_position_classifier.feature_functions import all_features
from confusion_matrix import ConfusionMatrix, Alphabet
import config
import util


class Trainer(object):
    def __init__(self,
                classifier,
                model_path,
                feature_function_list,
                train_feature_path,
                dev_feature_path,
                dev_classifier_out_path):

        self.classifier = classifier
        self.model_path = model_path
        self.feature_function_list = feature_function_list
        self.train_feature_path = train_feature_path
        self.dev_feature_path = dev_feature_path
        self.dev_classifier_out_path = dev_classifier_out_path


    def make_feature_file(self, train_parse_dict, dev_parse_dict, train_connectives, dev_connectives):

        print("-"*120)
        print("\n".join([f.__name__ for f in feature_function_list]))
        print("-" * 120)

        print("make train feature_file file ...")
        Make_feature_file(train_parse_dict, train_connectives, self.feature_function_list, self.train_feature_path)
        print("make dev feature_file file ...")
        Make_feature_file(dev_parse_dict, dev_connectives, self.feature_function_list, self.dev_feature_path)

    def train_mode(self):
        self.classifier.train_model(self.train_feature_path, self.model_path)

    def test_model(self):
        self.classifier.test_model(self.dev_feature_path, self.dev_classifier_out_path, self.model_path)


def do_evaluation(dev_classifier_out_path):

    gold_list = util.get_mallet_gold_list(dev_classifier_out_path)
    predicted_list = util.get_mallet_predicted_list(dev_classifier_out_path)
    binary_alphabet = Alphabet()
    binary_alphabet.add('1')
    binary_alphabet.add('0')

    cm = util.compute_binary_eval_metric(predicted_list, gold_list, binary_alphabet)

    cm.print_out()

    return cm.get_accuracy()


def write_error_cases_to_file(dev_parse_dict, dev_feature_path, dev_classifier_out_path, to_file):
    with \
        open(dev_feature_path) as dev_feature_file, \
        open(dev_classifier_out_path) as dev_classifier_out_file, \
        open(to_file, "w") as fout:

        dev_features = [line.strip() for line in dev_feature_file if line.strip() != ""]
        predictions = [line.strip() for line in dev_classifier_out_file if line.strip() != ""]

        assert(len(dev_features) == len(predictions))

        # 被预测为0的,但其实是1的
        gold_ps_pred_ss = []
        # 被预测为1的,但其实是0的
        gold_ss_pred_ps = []

        for feat, pred in zip(dev_features, predictions):
            gold_label = feat.split(" ")[0]
            comment_list = feat.split(" # ")[-1].split("|")
            conn_name = comment_list[0]
            DocID = comment_list[1]
            sent_index = int(comment_list[2])
            conn_indices = comment_list[3].split(" ")

            fields = pred.split("\t")[1:]
            d = {}
            for i in range(len(fields)):
                if i % 2 == 0:
                    d[fields[i]] = float(fields[i+1])
            sort_label = sorted(d.items(), key=lambda x: x[1], reverse=True)
            pred_label = sort_label[0][0]

            sent = " ".join([word[0] for word in dev_parse_dict[DocID]["sentences"][sent_index]["words"]])

            if gold_label == "1" and pred_label == "0":
                case = "==" * 40 + "\n"
                case += "gold_ps_pred_ss\n"
                case += sent + "\n"
                case += "%s\t%s\t%s\t%s" % (DocID, str(sent_index), str(conn_indices), conn_name)

                gold_ps_pred_ss.append(case)

            if gold_label == "0" and pred_label == "1":
                case = "==" * 40 + "\n"
                case += "gold_ss_pred_ps\n"
                case += sent + "\n"
                case += "%s\t%s\t%s\t%s" % (DocID, str(sent_index), str(conn_indices), conn_name)

                gold_ss_pred_ps.append(case)

        fout.write("\n".join(gold_ps_pred_ss))
        fout.write("\n")
        fout.write("\n".join(gold_ss_pred_ps))


if __name__ == "__main__":

    # feature_file function list
    feature_function_list = [
       all_features
    ]

    ''' classifier '''
    classifier = Mallet_classifier(MaxEnt())


    ''' model path '''
    model_path = config.ARG_POSITION_CLASSIFIER_MODEL

    ''' train feature_file & test feature_file & test result path '''
    train_feature_path = config.ARG_POSITION_TRAIN_FEATURE_OUTPUT_PATH
    dev_feature_path = config.ARG_POSITION_DEV_FEATURE_OUTPUT_PATH
    dev_classifier_out_path = config.ARG_POSITION_DEV_OUTPUT_PATH

    ''' Trainer '''
    trainer = Trainer(classifier, model_path, feature_function_list, train_feature_path, dev_feature_path, dev_classifier_out_path)


    # load data ...

    with \
        open(config.TRAIN_PATH + "pdtb-parses.json") as train_parse_file, \
        open(config.DEV_PATH + "pdtb-parses.json") as dev_parse_file, \
        open(config.DATA_PATH + "ss_vs_ps_conn/train/ss_vs_ps_conn.pkl", "rb") as train_pkl_file, \
        open(config.DATA_PATH + "ss_vs_ps_conn/dev/ss_vs_ps_conn.pkl", "rb") as dev_pkl_file:

        train_parse_dict = json.load(train_parse_file)
        dev_parse_dict = json.load(dev_parse_file)
        print("parse dict is loaded...")
        train_connectives = pickle.load(train_pkl_file)
        dev_connectives = pickle.load(dev_pkl_file)
        print("connective is loaded...")

        # make feature_file file
        trainer.make_feature_file(train_parse_dict, dev_parse_dict, train_connectives, dev_connectives)
        # train
        trainer.train_mode()
        # test
        trainer.test_model()

    # do evaluation
    do_evaluation(dev_classifier_out_path)

    err_case_path = config.CWD+"tmp/arg_position_error_cases.txt"
    write_error_cases_to_file(dev_parse_dict, dev_feature_path, dev_classifier_out_path, err_case_path)
