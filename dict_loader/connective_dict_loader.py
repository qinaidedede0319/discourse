from util import singleton
import util, config


@singleton
class Connectives_dict_loader(object):
    def __init__(self):
        self.sorted_conns_list = util.load_list_from_file(config.SORTED_ExpConn_PATH)


        # lin
        self.dict_cpos = util.load_dict_from_file(config.CONNECTIVE_DICT_CPOS_PATH)
        self.dict_prev_C = util.load_dict_from_file(config.CONNECTIVE_DICT_PREV_C_PATH)
        self.dict_prevPOS = util.load_dict_from_file(config.CONNECTIVE_DICT_PREVPOS_PATH)
        self.dict_prePOS_CPOS = util.load_dict_from_file(config.CONNECTIVE_DICT_PREVPOS_CPOS_PATH)
        self.dict_C_next = util.load_dict_from_file(config.CONNECTIVE_DICT_C_NEXT_PATH)
        self.dict_nextPOS = util.load_dict_from_file(config.CONNECTIVE_DICT_NEXTPOS_PATH)
        self.dict_CPOS_nextPOS = util.load_dict_from_file(config.CONNECTIVE_DICT_CPOS_NEXTPOS_PATH)
        self.dict_CParent_to_root_path = util.load_dict_from_file(config.CONNECTIVE_DICT_CPARENT_TO_ROOT_PATH)
        self.dict_compressed_cparent_to_root_path = util.load_dict_from_file(config.CONNECTIVE_DICT_COMPRESSED_CPARENT_TO_ROOT_PATH)
        # pitler
        self.dict_self_category = util.load_dict_from_file(config.CONNECTIVE_DICT_SELF_CATEGORY_PATH)
        self.dict_parent_category = util.load_dict_from_file(config.CONNECTIVE_DICT_PARENT_CATEGORY_PATH)
        self.dict_left_sibling_category = util.load_dict_from_file(config.CONNECTIVE_DICT_LEFT_SIBLING_CATEGORY_PATH)
        self.dict_right_sibling_category = util.load_dict_from_file(config.CONNECTIVE_DICT_RIGHT_SIBLING_CATEGORY_PATH)
        # conn - syn
        self.dict_conn_self_category = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_SELF_CATEGORY_PATH)
        self.dict_conn_parent_category = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_PARENT_CATEGORY_PATH)
        self.dict_conn_left_sibling_category = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_LEFT_SIBLING_CATEGORY_PATH)
        self.dict_conn_right_sibling_category = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_RIGHT_SIBLING_CATEGORY_PATH)
        # syn-syn
        self.dict_self_parent = util.load_dict_from_file(config.CONNECTIVE_DICT_SELF_PARENT_CATEGORY_PATH)
        self.dict_self_right = util.load_dict_from_file(config.CONNECTIVE_DICT_SELF_RIGHT_CATEGORY_PATH)
        self.dict_self_left = util.load_dict_from_file(config.CONNECTIVE_DICT_SELF_LEFT_CATEGORY_PATH)
        self.dict_parent_left = util.load_dict_from_file(config.CONNECTIVE_DICT_PARENT_LEFT_CATEGORY_PATH)
        self.dict_parent_right = util.load_dict_from_file(config.CONNECTIVE_DICT_PARENT_RIGHT_CATEGORY_PATH)
        self.dict_left_right = util.load_dict_from_file(config.CONNECTIVE_DICT_LEFT_RIGHT_CATEGORY_PATH)

        # mine
        self.dict_conn_name = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN)
        self.dict_conn_lower_case = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_LOWER_CASE)
        self.dict_CParent_to_root_path_node_names = util.load_dict_from_file(config.CONNECTIVE_DICT_CPARENT_TO_ROOT_PATH_NODE_NAMES)

        self.dict_conn_connCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_CONNCTX)
        self.dict_conn_connLinkedCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_CONNLINKEDCTX)

        self.dict_conn_rightSiblingCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_RIGHTSIBLINGCTX)
        self.dict_conn_rightSiblingLinkedCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_RIGHTSIBLINGLINKEDCTX)

        self.dict_conn_leftSiblingCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_LEFTSIBLINGCTX)
        self.dict_conn_leftSiblingLinkedCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_LEFTSIBLINGLINKEDCTX)

        self.dict_conn_parent_categoryCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_PARENT_CATEGORYCTX)
        self.dict_conn_parent_categoryLinkedCtx = util.load_dict_from_file(config.CONNECTIVE_DICT_CONN_PARENT_CATEGORYLINKEDCTX)





if __name__ == "__main__":
    print(Connectives_dict_loader().sorted_conns_list)
