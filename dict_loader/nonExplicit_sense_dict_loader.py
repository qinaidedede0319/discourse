import sys
sys.path.append("../")
import glob
import os
from util import singleton
import util, config

@singleton
class NonExplicit_sense_dict_loader(object):
    def __init__(self):
        self.dict_word_to_brown_cluster = self.get_dict_word_to_brown_cluster()

        self.dict_word_pairs= util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_WORD_PAIRS)
        self.dict_production_rules= util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_PRODUCTION_RULES)
        self.dict_dependency_rules= util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_DEPENDENCY_RULES)

        self.dict_Arg1_first = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG1_FIRST)
        self.dict_Arg1_last = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG1_LAST)
        self.dict_Arg2_first = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG2_FIRST)
        self.dict_Arg2_last = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG2_LAST)
        self.dict_Arg1_first_Arg2_first = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG1_FIRST_ARG2_FIRST)
        self.dict_Arg1_last_Arg2_last = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG1_LAST_ARG2_LAST)
        self.dict_Arg1_first3 = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG1_FIRST3)
        self.dict_Arg2_first3 = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_ARG2_FIRST3)

        self.dict_brown_cluster_pairs = util.load_dict_from_file(config.NON_EXPLICIT_SENSE_DICT_BROWN_CLUSTER_PAIRS)



    def get_dict_word_to_brown_cluster(self):

        with open(config.DICT_PATH + "/brown_cluster_3200.txt") as fin:
            d = {}
            for line in fin:
                c, w = line.strip().split("\t")
                d[w] = c
            return d

    def _get_dict_relationID_to_cnn_feature(self):

        d = {}

        for path in glob.glob(os.path.join(config.FEATURE_PATH, '*cnn*.txt')):
            with open(path) as fin:
                for line in fin:
                    if line.strip() == "":
                        continue
                    line_list = line.strip().split("\t")

                    ID = int(line_list[0])
                    feature = util.get_feature_by_list(list(map(float, line_list[1:])))

                    d[ID] = feature

        return d


