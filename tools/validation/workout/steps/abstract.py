from typing import List, Self, TypeAlias

from ..goals import AbstractWorkoutStepGoal, WorkoutStepGoals
from ..object import WorkoutObject
from ..utilities import collection_is_similar


OptionalGoals: TypeAlias =  List[AbstractWorkoutStepGoal] | WorkoutStepGoals | None

class AbstractWorkoutStep(WorkoutObject):

    def __init__(self, value, minimum=None, maximum=None, notes: str | None = None, goals: OptionalGoals = None):
        super().__init__()

        if value is None:
            if maximum is not None:
                if minimum is not None:
                    value = int((maximum - minimum) / 2 + minimum)
                else:
                    value = maximum
            #elif minimum is not None:
                #raise RuntimeError("No maximum value")
                #raise NoMaximumError
           # else:
                #raise RuntimeError("No target values")
                #raise NoTargetError

        self.value = value
        self.minimum = minimum
        self.maximum = maximum

        self.notes = notes
        if isinstance(goals, WorkoutStepGoals):
            self.goals = goals
        else:
            self.goals = WorkoutStepGoals.from_list(goals)
        # Goals should be a structure because there can only be one of each type
        # Also note that Garmin only supports 1 goal per step, and does not support
        # goals for repetitions. These additions are used here to make the process
        # more general, but will require some "selection" later to customize the 
        # final workout.

    def similar(self: Self, other: Self | None) -> bool:
        return super().similar(other) and \
            self.value == other.value and \
            self.minimum == other.minimum and \
            self.maximum == other.maximum and \
            self.notes == other.notes and \
            self.goals.similar(other.goals)