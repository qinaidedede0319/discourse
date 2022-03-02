class ConstituentArgument(object):
    def __init__(self, relationID, DocID, sent_index, connective, constituents):
        self.relationID = relationID
        self.DocID = DocID
        self.sent_index = sent_index # constituent 所在的 sentence index
        self.connective = connective
        self.constituents = constituents