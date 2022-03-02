#coding:utf-8

# clause object
class Arg_Clauses():
    def __init__(self, relation_ID, Arg, DocID, sent_index, clauses):
        self.relation_ID = relation_ID
        self.Arg = Arg
        self.DocID = DocID
        self.sent_index = sent_index
        self.clauses = clauses # [([1,2,3],yes), ([4, 5],no), ]
        self.conn_indices = None
        self.conn_head_name = None

class Clause(object):

    def __init__(self, DocID, sent_index, clause_indices, index):

        self.DocID = DocID
        self.sent_index = sent_index
        self.clause_indices = clause_indices
        self.index = index # 句子的第几个Clause
        self.label = None
        self.all_clauses = None
        self.clauses = None # 不等同于上面的all_clauses，实际形式是[([1,2,3],yes), ([4, 5],no), ]
        # 对于Explicit的PS
        self.connective = None