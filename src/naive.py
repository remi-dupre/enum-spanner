from mapping import is_valid_mapping
from va import VA, Variable


def naive_enum_matchings(va: VA, text: str):
    # The heap contains tuples (state, curr_char, assignation)
    heap = [(va.initial, 0, [])]

    while heap:
        state, curr_char, assignation = heap.pop()

        if curr_char == len(text) and is_valid_mapping(va.variables, assignation):
            yield assignation

        for label, target in va.adj[state]:
            if isinstance(label, Variable.Marker):
                new_assignation = assignation.copy()
                new_assignation.append((label, curr_char))
                heap.append((target, curr_char, new_assignation))
            elif curr_char < len(text) and label in ['*', text[curr_char]]:
                heap.append((target, curr_char + 1, assignation))
