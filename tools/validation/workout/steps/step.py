from typing import Self

from .abstract import AbstractWorkoutStep, OptionalGoals
from ..utilities import compress_values, values_are_compressible


class WorkoutStep(AbstractWorkoutStep):

    def __init__(self, value=None, minimum=None, maximum=None, unit: str = 'meters', goals: OptionalGoals = None, notes: str | None = None):
        super().__init__(value=value, minimum=minimum, maximum=maximum, goals=goals, notes=notes)
        self.unit = unit

    # value: Optional[Union[int, float]]
    # unit: Optional[str] = field(metadata={"validate": validate.OneOf(["seconds", "meters", "miles"])})

    #@override
    def similar(self: Self, other: Self | None) -> bool:
        return super().similar(other) and self.unit == other.unit
    
    @property
    def is_compressible(self) -> bool:
        if self.goals is not None and self.goals.is_compressible:
            return True
        
        if values_are_compressible(self.value, self.minimum, self.maximum):
            return True
        # # min == max -> compressible
        # # min == value & no-max -> compressible
        # # no-min & value == max -> compressible
        # if self.minimum is not None:
        #     if self.maximum is not None:
        #         if self.minimum == self.maximum:
        #             return True # Remove min and max
        #     elif self.value is not None:
        #         if self.minimum == self.value:
        #             return True # Remove min
        # elif self.maximum is not None:  # No minimum, but there is a maximum
        #     if self.value is not None:
        #         if self.maximum == self.value:
        #             return True # Remove min 
        # else:
        
        # I'm leaving this out as a reminder
        if self.notes is not None and len(self.notes) < 1:
            return True
        
        return False

    def compressed(self) -> Self | None:
        """
        Returns a compressed copy (or self).
        """
        if not self.is_compressible:
            return self
        
        # Perform the compression
        goals = None
        if self.goals is not None:
            compressed_goals = self.goals.compressed()
        
        notes = None
        if self.notes is not None and len(self.notes) > 0:
            notes = self.notes

        (value, minimum, maximum) = compress_values(self.value, self.minimum, self.maximum)

        return Self(value=value, minimum=minimum, maximum=maximum, unit=self.unit, goals=goals, notes=notes)
    

# Note that yes, I could have a string 'type' here,  but I'm purposefully
# making the transition harder because I want to have some custom logic propose
# different warnings, etc.

class CoolDownWorkoutStep(WorkoutStep):
    pass

class RecoverWorkoutStep(WorkoutStep):
    pass

class RestWorkoutStep(WorkoutStep):
    pass

class RunWorkoutStep(WorkoutStep):
    pass

class WarmUpWorkoutStep(WorkoutStep):
    pass

