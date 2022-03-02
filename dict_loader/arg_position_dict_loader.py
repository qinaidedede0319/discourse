from util import singleton
import util, config

@singleton
class Arg_position_dict_loader(object):
    def __init__(self):
        self.dict_CString = util.load_dict_from_file(config.ARG_POSITION_DICT_CSTRING)
        self.dict_CPOS = util.load_dict_from_file(config.ARG_POSITION_DICT_CPOS)
        self.dict_prev1 = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV1)
        self.dict_prev1POS = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV1POS)
        self.dict_prev1_C = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV1_C)
        self.dict_prev1POS_CPOS = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV1POS_CPOS)
        self.dict_prev2 = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV2)
        self.dict_prev2POS = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV2POS)
        self.dict_prev2_C = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV2_C)
        self.dict_prev2POS_CPOS = util.load_dict_from_file(config.ARG_POSITION_DICT_PREV2POS_CPOS)

        self.dict_next1 = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT1)
        self.dict_next1POS = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT1POS)
        self.dict_next1_C = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT1_C)
        self.dict_next1POS_CPOS = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT1POS_CPOS)
        self.dict_next2 = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT2)
        self.dict_next2POS = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT2POS)
        self.dict_next2_C = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT2_C)
        self.dict_next2POS_CPOS = util.load_dict_from_file(config.ARG_POSITION_DICT_NEXT2POS_CPOS)

        self.dict_conn_to_root_path = util.load_dict_from_file(config.ARG_POSITION_DICT_CONN_TO_ROOT_PATH)
