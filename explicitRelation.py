
class ExplicitRelation(object):

    def __init__(self, connective):
        self.ID = None
        self.Type = "Explicit"
        self.connective = connective
        self.DocID = connective.DocID
        # [[92, 95, 15, 1, 0], [96, 99, 16, 1, 1], [100, 104, 17, 1, 2]]
        self.Arg1_TokenList = None
        self.Arg2_TokenList = None
        # "Sense": ["Expansion.Conjunction"]
        self.Sense = None
        # Sense Label: 0, 1, ...
        self.SenseLabel = None

