import sys
sys.path.append("../../")
from model_trainer.NT_arg_extractor.evaluation import get_Arg_acc
from model_trainer.NT_arg_extractor.make_feature_file import Make_feature_file
from model_trainer.mallet_classifier import *
import json, pickle
from model_trainer.NT_arg_extractor.feature_functions import all_features
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


    def make_feature_file(self, train_parse_dict, dev_parse_dict, train_constituentArguments, dev_constituentArguments):

        print("-"*120)
        print("\n".join([f.__name__ for f in feature_function_list]))
        print("-" * 120)

        print("make train feature_file file ...")
        Make_feature_file(train_parse_dict, train_constituentArguments, self.feature_function_list, self.train_feature_path)
        print("make dev feature_file file ...")
        Make_feature_file(dev_parse_dict, dev_constituentArguments, self.feature_function_list, self.dev_feature_path)


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
    binary_alphabet.add('2')

    cm = util.compute_binary_eval_metric(predicted_list, gold_list, binary_alphabet)

    cm.print_out()

    return cm.get_accuracy()


if __name__ == "__main__":

    # feature_file function list
    feature_function_list = [
        all_features
    ]

    ''' classifier '''
    classifier = Mallet_classifier(MaxEnt())

    ''' model path '''
    model_path = config.NT_CLASSIFIER_MODEL

    ''' train feature_file & test feature_file & test result path '''
    train_feature_path = config.NT_TRAIN_FEATURE_OUTPUT_PATH
    dev_feature_path = config.NT_DEV_FEATURE_OUTPUT_PATH
    dev_classifier_out_path = config.NT_DEV_OUTPUT_PATH

    ''' Trainer '''
    trainer = Trainer(classifier, model_path, feature_function_list, train_feature_path, dev_feature_path, dev_classifier_out_path)


    # load data ...

    with \
        open(config.TRAIN_PATH + "pdtb-parses.json") as train_parse_file, \
        open(config.DEV_PATH + "pdtb-parses.json") as dev_parse_file, \
        open(config.DATA_PATH + "ss_arg12_vs_null/train/ss_arg12_vs_null_constituentArguments.pkl", "rb") as train_pkl_file, \
        open(config.DATA_PATH + "ss_arg12_vs_null/dev/ss_arg12_vs_null_constituentArguments.pkl", "rb") as dev_pkl_file:

        train_parse_dict = json.load(train_parse_file)
        dev_parse_dict = json.load(dev_parse_file)
        print("parse dict is loaded...")
        train_constituentArguments = pickle.load(train_pkl_file)
        dev_constituentArguments = pickle.load(dev_pkl_file)
        print("constituentArguments is loaded...")

        # # make feature_file file
        # trainer.make_feature_file(train_parse_dict, dev_parse_dict, train_constituentArguments, dev_constituentArguments)
        # # train
        # trainer.train_mode()
        # # test
        # trainer.test_model()

    # do evaluation
    do_evaluation(dev_classifier_out_path)

    fin = open(config.DEV_PATH + "relations.json")
    dev_relations = [json.loads(x) for x in fin]
    fin.close()
    get_Arg_acc(dev_parse_dict, dev_relations, dev_feature_path, dev_classifier_out_path)
