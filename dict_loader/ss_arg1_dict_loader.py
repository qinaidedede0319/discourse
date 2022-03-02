from util import singleton
import util, config

@singleton
class SS_arg1_dict_loader(object):
    def __init__(self):

        ''' connective only '''
        self.dict_CON_Str = util.load_dict_from_file(config.SS_ARG1_DICT_CON_Str)
        self.dict_CON_LStr = util.load_dict_from_file(config.SS_ARG1_DICT_CON_LStr)
        self.dict_CON_POS = util.load_dict_from_file(config.SS_ARG1_DICT_CON_POS)
        self.dict_CParent_to_root_path = util.load_dict_from_file(config.SS_ARG1_DICT_CPARENT_TO_ROOT_PATH)
        self.dict_CParent_to_root_path_node_names = util.load_dict_from_file(config.SS_ARG1_DICT_CPARENT_TO_ROOT_PATH_NODE_NAMES)
        self.dict_conn_connCtx = util.load_dict_from_file(config.SS_ARG1_DICT_CONN_CONNCTX)
        self.dict_conn_rightSiblingCtx = util.load_dict_from_file(config.SS_ARG1_DICT_CONN_RIGHTSIBLINGCTX)
        self.dict_conn_parent_categoryCtx = util.load_dict_from_file(config.SS_ARG1_DICT_CONN_PARENT_CATEGORYCTX)
        self.dict_self_category = util.load_dict_from_file(config.SS_ARG1_DICT_SELF_CATEGORY)
        self.dict_parent_category = util.load_dict_from_file(config.SS_ARG1_DICT_PARENT_CATEGORY)
        self.dict_left_sibling_category = util.load_dict_from_file(config.SS_ARG1_DICT_LEFT_SIBLING_CATEGORY)
        self.dict_right_sibling_category = util.load_dict_from_file(config.SS_ARG1_DICT_RIGHT_SIBLING_CATEGORY)

        ''' constituent only '''
        self.dict_NT_Ctx = util.load_dict_from_file(config.SS_ARG1_DICT_NT_Ctx)
        self.dict_NT_Linked_ctx = util.load_dict_from_file(config.SS_ARG1_DICT_NT_LINKED_CTX)
        self.dict_NT_parent_ctx = util.load_dict_from_file(config.SS_ARG1_DICT_NT_PARENT_CTX)
        self.dict_NT_parent_linked_ctx = util.load_dict_from_file(config.SS_ARG1_DICT_NT_PARENT_LINKED_CTX)
        self.dict_NT_to_root_path = util.load_dict_from_file(config.SS_ARG1_DICT_NT_TO_ROOT_PATH)

        ''' connective <--> constituent '''
        self.dict_CON_NT_Path = util.load_dict_from_file(config.SS_ARG1_DICT_CON_NT_Path)
        self.dict_CON_NT_Path_iLsib = util.load_dict_from_file(config.SS_ARG1_DICT_CON_NT_Path_iLsib)

        ''' constituent <--> constituent '''
        self.dict_NT_prev_curr_path = util.load_dict_from_file(config.SS_ARG1_DICT_PREV_CURR_PATH)
        self.dict_NT_curr_next_path = util.load_dict_from_file(config.SS_ARG1_DICT_CURR_NEXT_PATH)



        self.dict_conn_to_category = self.get_dict_conn_to_category()



    def get_dict_conn_to_category(self):
        d = {}
        file = open(config.DICT_PATH + "/connective-category.txt")
        lines = [line.strip() for line in file.readlines()]
        for line in lines:
            list = line.split("#")
            conn = list[0].strip()
            category = list[1].strip()
            d[conn] = category
        return d