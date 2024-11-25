from typing import TypeVar, List, Tuple

# T really needs to be of a type that contains "SIMILAR", which really is WorkoutObject
T = TypeVar('T')

def collection_is_similar(first: List[T], second: List[T]) -> bool:
    if first is None:
        return second is None # Same is OK; different is not
    elif second is not None:
        return False  # First is None and second is not

    # They cannot be 'similar' if the lengths are different
    if len(first) != len(second):
        return False
    
    # We aren't interested in equal objects, just similar ones...
    for (first_obj, second_obj) in zip(first, second):
        if not first_obj.similar(second_obj):
            return False
        
    return True

N= TypeVar('N')
def compress_values(value: N | None, minimum: N | None,  maximum: N | None) -> Tuple[N | None, N | None, N | None]:
    new_min = minimum
    new_max = maximum
    new_value = value

    if new_min is not None:
        if new_value is not None:
            if new_max is not None:  # T, T, T
                if new_min == new_max:
                    new_min = None
                    new_max = None
            elif new_min == new_value: #  T, T, F 
                new_min = None
        elif new_max is not None and new_min == new_max:  # F, T, T Replace
            new_value = new_min
            new_min = None
            new_max = None
    elif new_value is not None and new_max is not None and new_value == new_max: #  T, F, T
        new_max = None

    return (new_min, new_value, new_max)

def values_are_compressible(value: N | None, minimum: N | None,  maximum: N | None) -> bool:
    if minimum is not None:
        if value is not None:
            if maximum is not None:  # T, T, T
                return minimum == maximum
            elif minimum == value: #  T, T, F 
                return True
        elif maximum is not None and minimum == maximum:  # F, T, T Replace
            return True
    elif value is not None and maximum is not None and value == maximum: #  T, F, T
        return True

    return False
