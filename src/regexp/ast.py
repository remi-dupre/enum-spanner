from lark import Token, Transformer


class EnumerateVariables(Transformer):
    #pylint: disable=no-self-use
    def named_group(self, children):
        children[0] = {str(children[0])}
        return set.union(*children)

    def __default__(self, data, children, meta):
        if not children:
            return set()

        for i, child in enumerate(children):
            if isinstance(child, Token):
                children[i] = set()

        return set.union(*children)
