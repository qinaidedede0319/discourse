from util import singleton
import util, config

@singleton
class PS_arg2_dict_loader(object):
    def __init__(self):

        ''' curr only '''
        self.dict_curr_lowercase_verbs = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_LOWERCASE_VERBS)
        self.dict_curr_first_lowercase_verb = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_LOWERCASE_VERB)
        self.dict_curr_lemma_verbs = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_LEMMA_VERBS)
        self.dict_curr_first_lemma_verb = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_LEMMA_VERB)
        self.dict_curr_first = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST)
        self.dict_curr_last = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_LAST)
        self.dict_curr_production_rule = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_PRODUCTION_RULE)
        self.dict_curr_position = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_POSITION)
        self.dict_2prev_pos_lemma_verb = util.load_dict_from_file(config.PS_ARG2_DICT_2PREV_POS_LEMMA_VERB)

        self.dict_curr_first_punctuations = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_PUNCTUATIONS)
        self.dict_curr_last_punctuations = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_LAST_PUNCTUATIONS)

        self.dict_prev_first_curr_first = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_FIRST_CURR_FIRST)
        self.dict_prev_last_curr_last = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_LAST_CURR_LAST)
        self.dict_curr_first_next_first = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_NEXT_FIRST)
        self.dict_curr_last_next_last = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_LAST_NEXT_LAST)

        self.dict_prev_first = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_FIRST)
        self.dict_next_last = util.load_dict_from_file(config.PS_ARG2_DICT_NEXT_LAST)

        self.dict_curr_first_last = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_LAST)
        self.dict_curr_first_punc_last_punc = util.load_dict_from_file(
            config.PS_ARG2_DICT_CURR_FIRST_PUNC_LAST_PUNCS)

        ''' clause <--> clause '''
        self.dict_prev_last = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_LAST)
        self.dict_next_first = util.load_dict_from_file(config.PS_ARG2_DICT_NEXT_FIRST)
        self.dict_prev_last_curr_first = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_LAST_CURR_FIRST)
        self.dict_curr_last_next_first = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_LAST_NEXT_FIRST)
        self.dict_prev_curr_production_rule = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_CURR_PRODUCTION_RULE)
        self.dict_prev_curr_CP_production_rule = util.load_dict_from_file(config.PS_ARG2_DICT_PREV_CURR_CP_PRODUCTION_RULE)
        self.dict_curr_next_CP_production_rule = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_NEXT_CP_PRODUCTION_RULE)
        self.dict_curr_first_to_prev_last_path = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_TO_PREV_LAST_PATH)
        self.dict_curr_first_curr_first_lemma_verb = util.load_dict_from_file(config.PS_ARG2_DICT_CURR_FIRST_CURR_FIRST_LEMMA_VERB)

        ''' connective only '''
        self.dict_con_str = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_STR)
        self.dict_con_lstr = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_LSTR)
        self.dict_con_cat = util.load_dict_from_file(config.PS_ARG2_DICT_CON_CAT)
        self.dict_CParent_to_root_path_node_names = util.load_dict_from_file(config.PS_ARG2_DICT_CPARENT_TO_ROOT_PATH_NODE_NAMES)
        self.dict_CPOS = util.load_dict_from_file(config.PS_ARG2_DICT_CPOS)
        self.dict_conn_connCtx = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_CONNCTX)
        self.dict_conn_parent_category_Ctx = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_PARENT_CATEGORY_CTX)
        self.dict_conn_to_root_path = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_TO_ROOT_PATH)
        self.dict_conn_to_root_compressed_path = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_TO_ROOT_COMPRESSED_PATH)

        ''' connective <--> clause '''
        self.dict_conn_clause_position = util.load_dict_from_file(config.PS_ARG2_DICT_CLAUSE_CONN_POSITION)
        self.dict_conn_clause_distance = util.load_dict_from_file(config.PS_ARG2_DICT_CLAUSE_CONN_DISTANCE)
        self.dict_conn_position_distance = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_POSITION_DISTANCE)
        self.dict_conn_position = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_POSITION)
        self.dict_conn_is_adjacent_to_conn = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_IS_ADJACENT_TO_CONN)
        self.dict_conn_curr_first = util.load_dict_from_file(config.PS_ARG2_DICT_CONN_CURR_FIRST)

        ''' others '''
        self.dict_is_NNP_WP = util.load_dict_from_file(config.PS_ARG2_DICT_IS_NNP_WP)
        self.dict_is_curr_NNP_prev_PRP_or_NNP = util.load_dict_from_file(config.PS_ARG2_DICT_IS_CURR_NNP_PREV_PRP_OR_NNP)
        self.dict_is_contain_comma_which = util.load_dict_from_file(config.PS_ARG2_DICT_IS_CONTAIN_COMMA_WHICH)