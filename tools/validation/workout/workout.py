from typing import Self

from .steps import AbstractWorkoutStep
from .utilities import collection_is_similar

class Workout(object):
    """
    Workout is the top level object.  It starts with a list of steps. 
    The first step may be repetition, which makes the workout seem useless,
    but it's not!
    """
    
    def __init__(self, name: str | None = None, steps: list[AbstractWorkoutStep] | None = [], notes: str | None = None ):
        self.name = name
        self.steps = steps
        self.notes = notes
        
    #  def to_dict():
    #     data = {}
    #     if self.name is not None:
    #         data[NAME_KEY] = self.name
    #     data[STEPS_KEY] = [x.to_dict() for x in self.steps]

    def to_str(self, depth: int = 0) -> str:
        components = [x.to_str(depth + 1) for x in self.steps]
        return "Workout:\n{}".format('\n'.join(components))
    
    def similar(self: Self, other: Self | None) -> bool:
        if other is None:
            return False

        return self.name == other.name and collection_is_similar(self.steps, other.steps) and self.notes == other.notes
    
    def compressed(self) -> Self | None:
        """
        Returns a compressed copy (or self). If the workout is empty after 
        compression, then None is returned.
        """
       
        return self
