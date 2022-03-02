from util import singleton
import util, config

@singleton
class Implicit_arg1_dict_loader(object):
    def __init__(self):

        ''' curr only '''
        self.dict_curr_lowercase_verbs = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_LOWERCASE_VERBS)
        self.dict_curr_first_lowercase_verb = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_LOWERCASE_VERB)
        self.dict_curr_lemma_verbs = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_LEMMA_VERBS)
        self.dict_curr_first_lemma_verb = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_LEMMA_VERB)
        self.dict_curr_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST)
        self.dict_curr_last = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_LAST)
        self.dict_curr_production_rule = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_PRODUCTION_RULE)
        self.dict_curr_position = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_POSITION)
        self.dict_2prev_pos_lemma_verb = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_2PREV_POS_LEMMA_VERB)


        self.dict_curr_first_punctuations = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_PUNCTUATIONS)
        self.dict_curr_last_punctuations = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_LAST_PUNCTUATIONS)

        self.dict_prev_first_curr_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_FIRST_CURR_FIRST)
        self.dict_prev_last_curr_last = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_LAST_CURR_LAST)
        self.dict_curr_first_next_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_NEXT_FIRST)
        self.dict_curr_last_next_last = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_LAST_NEXT_LAST)

        self.dict_prev_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_FIRST)
        self.dict_next_last = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_NEXT_LAST)

        self.dict_curr_first_last = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_LAST)
        self.dict_curr_first_punc_last_punc = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_PUNC_LAST_PUNCS)

        ''' clause <--> clause '''
        self.dict_prev_last = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_LAST)
        self.dict_next_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_NEXT_FIRST)
        self.dict_prev_last_curr_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_LAST_CURR_FIRST)
        self.dict_curr_last_next_first = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_LAST_NEXT_FIRST)
        self.dict_prev_curr_production_rule = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_CURR_PRODUCTION_RULE)
        self.dict_prev_curr_CP_production_rule = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_CURR_CP_PRODUCTION_RULE)
        self.dict_curr_next_CP_production_rule = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_NEXT_CP_PRODUCTION_RULE)
        self.dict_curr_first_to_prev_last_path = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_TO_PREV_LAST_PATH)
        self.dict_curr_first_curr_first_lemma_verb = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_FIRST_CURR_FIRST_LEMMA_VERB)

        ''' others '''
        self.dict_is_NNP_WP = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_IS_NNP_WP)
        self.dict_is_curr_NNP_prev_PRP_or_NNP = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_IS_CURR_NNP_PREV_PRP_OR_NNP)
        self.dict_is_contain_comma_which = util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_IS_CONTAIN_COMMA_WHICH)