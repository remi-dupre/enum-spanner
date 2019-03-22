

class Match:

    def __init__(self, document, span: tuple, groups: dict):
        self.document = document
        self.span = span
        self.group_spans = groups

    @property
    def string(self):
        begin, end = self.span
        return self.document[begin:end]

    def __repr__(self):
        return f'Match(span={self.span}, match=\'{self.string}\')'
