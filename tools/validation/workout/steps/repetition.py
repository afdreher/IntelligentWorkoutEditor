from typing import Self

from .abstract import AbstractWorkoutStep
from ..goals import AbstractWorkoutStepGoal
from ..utilities import collection_is_similar


class RepetitionStep(AbstractWorkoutStep):

    def __init__(self, value, minimum=None, maximum=None, steps: list[AbstractWorkoutStep] = [], notes: str | None = None, goals: list[AbstractWorkoutStepGoal] | None = None):
        super().__init__(value=value, minimum=minimum, maximum=maximum, notes=notes, goals=goals)

        if len(steps) < 1:
             raise RuntimeError("No steps")
        self.steps = steps

    #@override
    def similar(self: Self, other: Self | None) -> bool:
        return super().similar(other) and collection_is_similar(self.steps, other.steps)
