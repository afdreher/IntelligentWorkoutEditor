from typing import Any, Self, List
from .object import WorkoutObject
from .constants import keys as KEYS


class AbstractWorkoutStepGoal(WorkoutObject):
    # If everything is null, then we don't need this goal
    def __init__(self, value=None, minimum=None, maximum=None):
        self.value = value
        self.minimum = minimum
        self.maximum = maximum

    # This is necessary because the LLM will sometimes hallucianate a goal, but is still "smart" enough to leave the fields empty
    @property
    def is_empty(self) -> bool:
        return self.value is None and self.minimum is None and self.maximum is None

    def similar(self: Self, other: Self | None) -> bool:
        return super().similar(other) and \
            self.value == other.value and \
            self.minimum == other.minimum and \
            self.maximum == other.maximum
            
    # def to_str(self, depth: int = 0) -> str:
    #     return "{}Goal ({}): {} {} {}".format(get_spacer(depth),self.goal_type, self.value, self.min, self.max)

class CadenceGoal(AbstractWorkoutStepGoal):
    """
    Class to hold cadence goals. Values are strides per minute
    """
    pass

class HeartRateGoal(AbstractWorkoutStepGoal):
    """
    Class to hold heart rate goals. Values are given in beats per minute
    """
    pass

    # Flag suspicious beats per minute such as <30 or >200
    # Allow it, but give the chatbot the ability to prompt and clear the warning

class HeartRateZoneGoal(AbstractWorkoutStepGoal):
    """
    Class to hold heart rate zone goals. Values should be 1-5 inclusive
    """
    pass

class LapTimeGoal(AbstractWorkoutStepGoal):
    """
    Class to hold lap time goals. Values are given in seconds.
    """
    pass

class PowerGoal(AbstractWorkoutStepGoal):
    """
    Class to hold power goals. Values are in watts
    """
    pass

class SpeedGoal(AbstractWorkoutStepGoal):
    """
    Class to hold speed and pace goals. Values are given in m/s
    """
    pass


class WorkoutStepGoals(WorkoutObject):
    """
    Workout goals are a collection of goals.  Note that only very basic checking
    is performed at this stage. Generally speaking, watches only allow ONE of
    these to be active. We'll handle /that/ issue when converting from the 
    Workout into a specific format.
    """

    def  __init__(
           self, 
           cadence: CadenceGoal | None = None,
           heart_rate: HeartRateGoal | None = None, 
           heart_rate_zone: HeartRateZoneGoal | None = None, 
           lap_time: LapTimeGoal | None = None,
           power: PowerGoal | None = None,
           speed : SpeedGoal | None = None
    ) -> Self:
        self.cadence = cadence
        self.heart_rate = heart_rate
        self.heart_rate_zone = heart_rate_zone
        self.lap_time = lap_time
        self.power = power
        self.speed = speed

    @classmethod
    def from_list(cls, goals: List[AbstractWorkoutStepGoal] | None) -> Self:    
        obj = WorkoutStepGoals()
        if goals is not None:
            for goal in goals:
                if isinstance(goal, CadenceGoal):
                    obj.cadence = goal
                elif isinstance(goal, HeartRateGoal):
                    obj.heart_rate = goal
                elif isinstance(goal, HeartRateZoneGoal):
                    obj.heart_rate_zone = goal
                elif isinstance(goal, LapTimeGoal):
                    obj.lap_time = goal
                elif isinstance(goal, SpeedGoal):
                    obj.speed = goal
                # Report unknown goal type

        return obj

    @property
    def __all_goals(self) -> List[AbstractWorkoutStepGoal]:
        return [
            self.cadence,
            self.heart_rate,
            self.heart_rate_zone,
            self.lap_time,
            self.power,
            self.speed
        ]

    @property
    def goals(self) -> List[AbstractWorkoutStepGoal] | None:
        result = filter(lambda x: x is not None and not x.is_empty, self.__all_goals)
        if len(result) > 0:
            return result
        return None

    @property
    def is_empty(self) -> bool:
        return not any(lambda x: x is not None and not x.is_empty, self.__all_goals)

    def similar(self: Self, other: Self | None) -> bool:
        if not super().similar(other):
            return False

        for (self_goal, other_goal) in zip(self.__all_goals, other.__all_goals):
            if self_goal is None:
                if other_goal is not None:
                    return False
            elif not self_goal.similar(other_goal):
                return False
            
        return True
    
    def __getitem__(self, key: str) -> AbstractWorkoutStepGoal | None:
        if key == KEYS.CADENCE:
            return self.cadence
        elif key == KEYS.HEART_RATE:
            return self.heart_rate
        elif key == KEYS.HEART_RATE_ZONE:
            return self.heart_rate_zone
        elif key == KEYS.LAP_TIME:
            return self.lap_time
        elif key == KEYS.POWER:
            return self.power
        elif key == KEYS.SPEED:
            return self.speed
        
        raise KeyError
    
    def __setitem__(self, key: str, value: AbstractWorkoutStepGoal):
        if key == KEYS.CADENCE:
            self.__check_type(value, CadenceGoal)
            self.cadence = value
        elif key == KEYS.HEART_RATE:
            self.__check_type(value, HeartRateGoal)
            self.heart_rate = value
        elif key == KEYS.HEART_RATE_ZONE:
            self.__check_type(value, HeartRateZoneGoal)
            self.heart_rate_zone = value
        elif key == KEYS.LAP_TIME:
            self.__check_type(value, LapTimeGoal)
            self.lap_time = value
        elif key == KEYS.POWER:
            self.__check_type(value, PowerGoal)
            self.power = value
        elif key == KEYS.SPEED:
            self.__check_type(value, SpeedGoal)
            self.speed = value

        raise KeyError
    
    def __check_type(self, value: object, class_or_tuple):
        """Helper method to throw TypeError if there is a mismatch"""
        if not isinstance(value, class_or_tuple):
            raise TypeError
        
    def compressed(self) -> Self | None:
        if self.is_empty:
            return None
        return self