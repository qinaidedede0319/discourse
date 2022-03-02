import sys
sys.path.append("../../")
from model_trainer.Explicit_classifier.make_feature_file import Make_feature_file
from model_trainer.mallet_classifier import *
import json, pickle
from model_trainer.Explicit_classifier.feature_functions import all_features
from confusion_matrix import ConfusionMatrix, Alphabet
import config
import util
import os

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

    def make_feature_file(self, train_parse_dict, dev_parse_dict, train_explicitRelations, dev_explicitRelations):

        print("-"*120)
        print("\n".join([f.__name__ for f in feature_function_list]))
        print("-" * 120)

        print("make train feature_file file ...")
        Make_feature_file(train_parse_dict, train_explicitRelations, self.feature_function_list, self.train_feature_path)
        print("make dev feature_file file ...")
        Make_feature_file(dev_parse_dict, dev_explicitRelations, self.feature_function_list, self.dev_feature_path)


    def train_mode(self):
        self.classifier.train_model(self.train_feature_path, self.model_path)

    def test_model(self):
        self.classifier.test_model(self.dev_feature_path, self.dev_classifier_out_path, self.model_path)


def do_evaluation(dev_classifier_out_path):

    gold_list = util.get_mallet_gold_list(dev_classifier_out_path)
    predicted_list = util.get_mallet_predicted_list(dev_classifier_out_path)
    binary_alphabet = Alphabet()
    for label in config.Label_To_Sense.keys():
        binary_alphabet.add(str(label))
    cm = util.compute_binary_eval_metric(predicted_list, gold_list, binary_alphabet)

    cm.print_out()
    print("Acc: %f" % cm.get_accuracy())



    # 使用scorer.py

    # dev gold explicit relations
    fin = open(config.DEV_PATH + "gold_explicit_relations_deleted.json")
    gold_explicit_relations = [json.loads(x) for x in fin]
    fin.close()

    dict_ID_to_relation = {}
    for relation in gold_explicit_relations:
        dict_ID_to_relation[relation["ID"]] = relation

    fin = open(config.EXPLICIT_DEV_FEATURE_OUTPUT_PATH)
    predicted_ID_list = [int(line.strip().split(" # ")[-1].split("|")[0]) for line in fin]
    fin.close()

    predicted_relations = []
    for pred, pred_ID in zip(predicted_list, predicted_ID_list):
        pred_sense = config.Label_To_Sense[pred]
        corresponding_relation = dict_ID_to_relation[pred_ID]

        corresponding_relation["Sense"] = [pred_sense]
        corresponding_relation["Arg1"]["TokenList"] = [item[2] for item in corresponding_relation["Arg1"]["TokenList"]]
        corresponding_relation["Arg2"]["TokenList"] = [item[2] for item in corresponding_relation["Arg2"]["TokenList"]]
        corresponding_relation["Connective"]["TokenList"] = [item[2] for item in corresponding_relation["Connective"]["TokenList"]]

        predicted_relations.append(corresponding_relation)

    fout = open(config.CWD + "dev_classifier_out/predicted_explict_sense.json", 'w')
    for relation in predicted_relations:
        fout.write('%s\n' % json.dumps(relation))
    fout.close()

    # by scorer.py
    cmd = "python %s %s %s" % (config.SCORER_PATH + "/scorer.py",
                               config.DEV_PATH + "gold_explicit_relations_deleted.json",
                               config.DEV_CLASSIFIER_OUT_PATH + "/predicted_explict_sense.json")

    # Precision 0.9227 Recall 0.9227 F1 0.9227\n
    out_lines = os.popen(cmd).readlines()
    F1 = out_lines[-1].strip().split(" ")[-1]

    print("".join(out_lines))

    print("F1: %f" % float(F1) )

    return cm.get_accuracy()


def write_error_cases_to_file(dev_parse_dict, dev_relations, dev_feature_path, dev_classifier_out_path, to_file):
    with \
        open(dev_feature_path) as dev_feature_file, \
        open(dev_classifier_out_path) as dev_classifier_out_file, \
        open(to_file, "w") as fout:

        dev_features = [line.strip() for line in dev_feature_file if line.strip() != ""]
        predictions = [line.strip() for line in dev_classifier_out_file if line.strip() != ""]

        assert(len(dev_features) == len(predictions))

        dict_relationID_to_relation = {}
        for relation in dev_relations:
            relationID = relation["ID"]
            dict_relationID_to_relation[relationID] = relation


        error_cases = []

        for feat, pred in zip(dev_features, predictions):
            gold_label = int(feat.split(" ")[0])
            comment_list = feat.split(" # ")[-1].split("|")
            relationID = int(comment_list[0])
            conn_name = comment_list[1]
            DocID = comment_list[2]
            sent_index = int(comment_list[3])
            conn_indices = comment_list[4].split(" ")

            fields = pred.split("\t")[1:]
            d = {}
            for i in range(len(fields)):
                if i % 2 == 0:
                    d[fields[i]] = float(fields[i+1])
            sort_label = sorted(d.items(), key=lambda x: x[1], reverse=True)
            pred_label = int(sort_label[0][0])

            gold_relation = dict_relationID_to_relation[relationID]
            Arg1 = gold_relation["Arg1"]["RawText"]
            Arg2 = gold_relation["Arg2"]["RawText"]


            if gold_label != pred_label:
                gold_sense = config.Label_To_Sense[str(gold_label)]
                pred_sense = config.Label_To_Sense[str(pred_label)]

                case = "==" * 40 + "\n"
                case += "%s --> %s\n" % (gold_sense, pred_sense)
                case += "Arg1: %s \n" % Arg1
                case += "Arg2: %s \n" % Arg2
                case += "%s\t%s\t%s\t%s" % (DocID, str(sent_index), str(conn_indices), conn_name)

                error_cases.append(case)


        fout.write("\n".join(error_cases))


if __name__ == "__main__":

    # feature_file function list
    feature_function_list = [
        all_features
    ]

    ''' classifier '''
    classifier = Mallet_classifier(MaxEnt())

    ''' model path '''
    model_path = config.EXPLICIT_CLASSIFIER_MODEL

    ''' train feature_file & test feature_file & test result path '''
    train_feature_path = config.EXPLICIT_TRAIN_FEATURE_OUTPUT_PATH
    dev_feature_path = config.EXPLICIT_DEV_FEATURE_OUTPUT_PATH
    dev_classifier_out_path = config.EXPLICIT_DEV_OUTPUT_PATH

    ''' Trainer '''
    trainer = Trainer(classifier, model_path, feature_function_list, train_feature_path, dev_feature_path, dev_classifier_out_path)


    # load data ...

    with \
        open(config.TRAIN_PATH + "pdtb-parses.json") as train_parse_file, \
        open(config.DEV_PATH + "pdtb-parses.json") as dev_parse_file, \
        open(config.DATA_PATH + "explicitRelations/train/explicitRelations.pkl", "rb") as train_pkl_file, \
        open(config.DATA_PATH + "explicitRelations/dev/explicitRelations.pkl", "rb") as dev_pkl_file:

        train_parse_dict = json.load(train_parse_file)
        dev_parse_dict = json.load(dev_parse_file)
        print("parse dict is loaded...")
        train_explicitRelations = pickle.load(train_pkl_file)
        dev_explicitRelations = pickle.load(dev_pkl_file)
        print("connective is loaded...")

        # make feature_file file
        trainer.make_feature_file(train_parse_dict, dev_parse_dict, train_explicitRelations, dev_explicitRelations)
        # train
        trainer.train_mode()
        # test
        trainer.test_model()

    # do evaluation
    do_evaluation(dev_classifier_out_path)

    fin = open(config.DEV_PATH + "relations.json")
    dev_relations = [json.loads(x) for x in fin]
    fin.close()
    err_case_path = config.CWD+"tmp/explictRelation_error_cases.txt"
    write_error_cases_to_file(dev_parse_dict, dev_relations, dev_feature_path, dev_classifier_out_path, err_case_path)
