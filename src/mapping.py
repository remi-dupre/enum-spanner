from va import Variable


def is_valid_mapping(variables, mapping):
    # Dictionnaries containing index for left and right bounds
    bounds = {Variable.Marker.Type.OPEN: dict(),
              Variable.Marker.Type.CLOSE: dict()}

    for x, i in mapping:
        # False if there is already a marker of this kind
        if x.variable in bounds[x.type]:
            return False

        bounds[x.type][x.variable] = i

    for v in variables:
        if (v not in bounds[Variable.Marker.Type.OPEN] or
                v not in bounds[Variable.Marker.Type.CLOSE] or
                bounds[Variable.Marker.Type.OPEN][v] > bounds[Variable.Marker.Type.CLOSE][v]):
            return False

    return True
