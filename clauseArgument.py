class ClauseArgument(object):
    def __init__(self, relationID, DocID, sent_index, clauses):
        self.relationID = relationID
        self.DocID = DocID
        self.sent_index = sent_index # clause 所在的 sentence index
        self.clauses = clauses
