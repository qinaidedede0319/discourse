from util import singleton
import util, config


@singleton
class Explicit_sense_dict_loader(object):
    def __init__(self):
        self.dict_CString = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CSTRING)
        self.dict_CPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CPOS)
        self.dict_C_Prev = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_C_PREV)

        self.dict_CLString = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CLSTRING)

        self.dict_self_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_SELF_CATEGORY_PATH)
        self.dict_parent_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_PARENT_CATEGORY_PATH)
        self.dict_left_sibling_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_LEFT_SIBLING_CATEGORY_PATH)
        self.dict_right_sibling_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_RIGHT_SIBLING_CATEGORY_PATH)

        self.dict_conn_self_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_SELF_CATEGORY_PATH)
        self.dict_conn_parent_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_PARENT_CATEGORY_PATH)
        self.dict_conn_left_sibling_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_LEFT_SIBLING_CATEGORY_PATH)
        self.dict_conn_right_sibling_category = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_RIGHT_SIBLING_CATEGORY_PATH)

        self.dict_self_parent = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_SELF_PARENT_CATEGORY_PATH)
        self.dict_self_right = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_SELF_RIGHT_CATEGORY_PATH)
        self.dict_self_left = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_SELF_LEFT_CATEGORY_PATH)
        self.dict_parent_left = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_PARENT_LEFT_CATEGORY_PATH)
        self.dict_parent_right = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_PARENT_RIGHT_CATEGORY_PATH)
        self.dict_left_right = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_LEFT_RIGHT_CATEGORY_PATH)


        ''' mine '''
        self.dict_as_prev_conn = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_AS_PREV_CONN)
        self.dict_as_prev_connPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_AS_PREV_CONNPOS)
        self.dict_when_prev_conn = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_WHEN_PREV_CONN)
        self.dict_when_prev_connPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_WHEN_PREV_CONNPOS)

        self.dict_prevPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_PREVPOS)
        self.dict_prePOS_CPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_PREPOS_CPOS)
        self.dict_C_next = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_C_NEXT)
        self.dict_nextPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_NEXTPOS)
        self.dict_CPOS_nextPOS = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CPOS_NEXTPOS)
        self.dict_CParent_to_root_path = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CPARENT_TO_ROOT_PATH)
        self.dict_compressed_cparent_to_root_path = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_COMPRESSED_CPARENT_TO_ROOT_PATH)
        self.dict_CParent_to_root_path_node_names = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CPARENT_TO_ROOT_PATH_NODE_NAMES)

        self.dict_conn_connCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_CONNCTX)
        self.dict_conn_connLinkedCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_CONNLINKEDCTX)

        self.dict_conn_rightSiblingCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_RIGHTSIBLINGCTX)
        self.dict_conn_rightSiblingLinkedCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_RIGHTSIBLINGLINKEDCTX)

        self.dict_conn_leftSiblingCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_LEFTSIBLINGCTX)
        self.dict_conn_leftSiblingLinkedCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_LEFTSIBLINGLINKEDCTX)

        self.dict_conn_parent_categoryCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_PARENT_CATEGORYCTX)
        self.dict_conn_parent_categoryLinkedCtx = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_CONN_PARENT_CATEGORYLINKEDCTX)

        ''' Arg1 Arg2 '''
        self.dict_Arg_verb_pairs = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_ARG_VERB_PAIRS)
        self.dict_Arg_first_verb_pair = util.load_dict_from_file(config.EXPLICIT_SENSE_DICT_ARG_FIRST_VERB_PAIR)