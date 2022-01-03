#coding:utf-8
import sys
import json
import codecs
import parser_util
import config


from model_trainer.connective_classifier.feature_functions \
    import all_features as _conn_clf_feature_function

from model_trainer.arg_position_classifier.feature_functions\
    import all_features as _arg_position_feature_function

from model_trainer.NT_arg_extractor.feature_functions \
    import all_features as _constituent_feat_func

from model_trainer.Explicit_classifier.feature_functions \
    import all_features as _explicit_feat_func

from model_trainer.Non_Explicit_classifier.feature_functions \
    import all_features as _non_explicit_feat_func, prev_context_conn


from model_trainer.PS_Arg2_extractor.feature_functions \
    import all_features as _ps_arg2_extractor_feat_func

from model_trainer.PS_Arg1_extractor.feature_functions \
    import all_features as _ps_arg1_extractor_feat_func

from model_trainer.Implicit_Arg1_extractor.feature_functions \
    import all_features as _implicit_arg1_feat_func

from model_trainer.Implicit_Arg2_extractor.feature_functions \
    import all_features as _implicit_arg2_feat_func


class DiscourseParser():
    def __init__(self, input_dataset, input_run):
        self.pdtb_parse = "{}/pdtb_trial_parses.json".format(input_dataset)
        self.raw_path = "{}/raw_train".format(input_dataset)
        self.input_run = input_run
        self.relations = []
        self.explicit_relations = []
        self.non_explicit_relations = []

        self.documents = json.loads(codecs.open(self.pdtb_parse, encoding="utf-8", errors="ignore").read())
        
        self.parse_dict = self.documents

        pass

    def parse(self):
        ## add paragraph info
        parser_util.add_paragraph_info_for_parse(self.parse_dict, self.raw_path)


        # obtain all connectives in documents
        # conns_list: [(DocID, sent_index, conn_indices), ()..]
        conns_list = parser_util.get_all_connectives(self.documents)

        ''' 1.1 Connective classifier '''

        print("==> Connective classifier:")
        
        conn_clf_feature_function = _conn_clf_feature_function
        conn_clf_feat_path = config.PARSER_CONN_CLF_FEATURE
        conn_clf_model_path = config.CONNECTIVE_CLASSIFIER_MODEL
        conn_clf_model_output = config.PARSER_CONN_CLF_MODEL_OUTPUT

        # extract features for each connective
        parser_util.conn_clf_print_feature(self.parse_dict, conns_list, conn_clf_feature_function, conn_clf_feat_path)
        # put feature file to corresponding model
        parser_util.put_feature_to_model(conn_clf_feat_path, conn_clf_model_path, conn_clf_model_output)
        # read model output, obtain the discourse connectives
        conns_list = parser_util.conn_clf_read_model_output(conn_clf_model_output, conns_list)

        ''' 1.2 Arg1 position classifier '''

        print ("\n==> Arg1 Position Classifier:")

        arg_position_feat_func = _arg_position_feature_function
        arg_position_feat_path = config.PARSER_ARG_POSITION_FEATURE
        arg_position_model_path = config.ARG_POSITION_CLASSIFIER_MODEL
        arg_position_model_output = config.PARSER_ARG_POSITION_MODEL_OUTPUT

        # extract features
        parser_util.arg_position_print_feature(self.parse_dict, conns_list, arg_position_feat_func, arg_position_feat_path)
        # put feature file to corresponding model
        parser_util.put_feature_to_model(arg_position_feat_path, arg_position_model_path, arg_position_model_output)
        # read model output
        # split the conns_list into SS_conns_list , PS_conns_list based on Arg1 Position Classifier
        SS_conns_list, PS_conns_list = parser_util.arg_position_read_model_output(arg_position_model_output, conns_list)

        ''' 1.3.1 SS Arguments Extractor '''

        print ("\n==> SS Arguments Extractor:")

        # split the SS_conns_list into SS_conns_parallel_list, SS_conns_not_parallel_list
        # parallel connectives: if..then; either..or;...
        # not parallel connectives: and; or; ...
        SS_conns_parallel_list, SS_conns_not_parallel_list = parser_util.divide_SS_conns_list(SS_conns_list)

        constituent_feat_func = _constituent_feat_func
        constituent_feat_path = config.PARSER_CONSTITUENT_FEATURE
        constituent_model_path = config.NT_CLASSIFIER_MODEL
        constituent_model_output = config.PARSER_CONSTITUENT_MODEL_OUTPUT

        # connectives: connective object list;
        # one connective object for each item of SS_conns_not_parallel_list
        connectives = parser_util.get_all_connectives_for_NT(self.parse_dict, SS_conns_not_parallel_list)
        # extract features for each constituent of each connective
        parser_util.constituent_print_feature(self.parse_dict, connectives, constituent_feat_func, constituent_feat_path)
        # put feature file to corresponding model
        parser_util.put_feature_to_model(constituent_feat_path, constituent_model_path, constituent_model_output)
        # read model output, obtain two Arguments for each not parallel connective
        # SS_conns_not_parallel_list_args: [("SS", DocID, sent_index, conn_indices, Arg1, Arg2)]
        SS_conns_not_parallel_list_args = \
            parser_util.constituent_read_model_output(            
                constituent_feat_path, constituent_model_output, self.parse_dict, SS_conns_not_parallel_list)
        # obtain two Arguments for each parallel connective by rules.
        SS_conns_parallel_list_args = parser_util.get_Args_for_SS_parallel_conns(self.parse_dict, SS_conns_parallel_list)



if __name__ == "__main__":
    
    # input_dataset = sys.argv[1]
    # input_run = sys.argv[2]
    # output_dir = sys.argv[3] 

    '''just test'''
    input_dataset = "./data/conll15st-trial-data-01-20-15"
    input_run = None
    output_dir = "./data/conll15st-trial-data-01-20-15"

    parser = DiscourseParser(input_dataset, input_run)
    parser.parse()
