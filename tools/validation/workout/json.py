from thefuzz import fuzz, process
import json
from typing import TypeAlias, List, Self, Tuple

from .constants import keys as KEYS
from .constants import types as TYPES

from .goals import AbstractWorkoutStepGoal, SpeedGoal, HeartRateGoal, HeartRateZoneGoal, CadenceGoal, PowerGoal, LapTimeGoal
from .steps import AbstractWorkoutStep, WorkoutStep, RunWorkoutStep, RecoverWorkoutStep, RestWorkoutStep, WarmUpWorkoutStep, CoolDownWorkoutStep
from .steps import RepetitionStep
from .workout import Workout

from .exceptions import InvalidGoalTypeError, InvalidStepTypeError



# Encode / Decode

DEFAULT_SCORE_THRESHOLD = 77

F: TypeAlias = float | None
def get_limits(data) -> Tuple[F, F, F]:
    # Support both min / minimum and max / maximum
    minimum = data.get(KEYS.MINIMUM) or data.get(KEYS.MIN)
    maximum = data.get(KEYS.MAXIMUM) or data.get(KEYS.MAX)
    value = data.get(KEYS.VALUE)

    # Check that min / max are valid
    if minimum is not None and maximum is not None and minimum > maximum:
        temp = minimum
        minimum = maximum
        maximum = temp

    return (minimum, maximum, value)


# Perform a fuzzy Levenshtein distance match to allow for a few spelling errors, etc.
def selectFuzzyMatch(target: str, options: List[str], score_cutoff: int = DEFAULT_SCORE_THRESHOLD):
    return process.extractOne(target, options, score_cutoff=score_cutoff)
 
def get_type_from_dict(data) -> str:
    return data[KEYS.TYPE].lower() # Raise key error if it's not present


class WorkoutDecoder(json.JSONDecoder):
    
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def decode(self, s, **kwargs):
        """
        Decode JSON from a string.
        
        This function is a wrapper around the usual decode function because we
        want to perform some post-processing steps.
        """

        # Just in case...  The LLM sometimes generates this since the template
        # uses the backticks to indicate code.
        s = s.strip('```') 

        # Decode the JSON string as usual
        obj = super().decode(s, **kwargs)

        # Obj *should* be a list, but in case it's not...
        if isinstance(obj, Workout):
            return obj
        elif isinstance(obj, list):
            return Workout(steps=obj)
        return Workout(steps=[obj])
    

    def object_hook(self, data):
        """Decode an object from a dictionary"""

        if KEYS.TYPE not in data:
            return data
        
        step_type = get_type_from_dict(data)
        
        # Otherwise... process the data as something else
        if step_type == TYPES.WORKOUT:
            return self.decode_workout(data)
        if step_type == TYPES.REPETITION:
            return self.decode_repetition(data)
        elif step_type in TYPES.WORKOUT_STEPS.keys():
            return self.decode_step(step_type, data)
            #return WorkoutStep.from_dict(data)
        elif step_type in TYPES.STEP_GOALS.keys():
            return self.decode_goal(step_type, data)
        else:
            # Run the more expensive fuzzy match step
            if fuzz.ratio(step_type, TYPES.REPETITION) >= DEFAULT_SCORE_THRESHOLD:
                #data[KEYS.TYPE] = TYPES.REPETITION  # Overwrite so that the dictionary matches
                return self.decode_repetition(data)
            elif (extracted := selectFuzzyMatch(step_type, TYPES.WORKOUT_STEPS.keys())) is not None:
                #data[KEYS.TYPE] = extracted[0] # Overwrite so that the dictionary matches
                return self.decode_step(extracted[0], data)
            elif (extracted := selectFuzzyMatch(step_type, TYPES.STEP_GOALS.keys())) is not None:
                return self.decode_goal(extracted[0], data)
        
        raise InvalidStepTypeError(step_type)


    def decode_workout(self, data):
        """Decode the workout"""
        # Get the steps and check their validity

        steps = data.get(KEYS.STEPS)
        if steps is None:
            raise ValueError('No steps provided')

        for step in data[KEYS.STEPS]:
            if not isinstance(step, AbstractWorkoutStep):
                # Flag error
                raise TypeError(f'{step} is not of type WorkoutStep')
            
        return Workout(
            name=self.stripped_value(data, KEYS.NAME),
            steps=steps,
            notes=self.stripped_value(data, KEYS.NOTES),
        )

    def check_goals(self, goals):
        """
        Check to make sure all of the objects are actually Goals.
        
        This is the most basic of the checks.  Further processing downstream
        will refine the types, positions, and whether or not the goals are 
        even satisfiable.
        """
        for goal in goals:
            if not isinstance(goal, AbstractWorkoutStepGoal):
                raise TypeError(f'{goal} is not of type AbstractWorkoutStepGoal')


    def decode_repetition(self, data):
        """Decode a repetition step"""
        # Get the steps and check their validity
        steps = data.get(KEYS.STEPS)
        if steps is None:
            raise ValueError('No steps provided')

        for step in data[KEYS.STEPS]:
            if not isinstance(step, AbstractWorkoutStep):
                # Flag error
                raise TypeError(f'{step} is not of type WorkoutStep')
            
        goals = data.get(KEYS.GOALS)
        if goals is not None:
            self.check_goals(goals)

        # Make sure that the steps data is the correct type
        (minimum, maximum, value) = get_limits(data)
        return RepetitionStep(
            value=value,
            minimum=minimum,
            maximum=maximum,
            steps=steps,
            notes=self.stripped_value(data, KEYS.NOTES),
            goals=goals,
        )
    

    def decode_step(self, step_type, data):
        """Decode an object corresponding to a workout step"""
        (minimum, maximum, value) = get_limits(data)
        args = {
            'minimum': minimum,
            'maximum': maximum,
            'value': value,
            'unit': self.stripped_value(data, KEYS.UNIT),
            'notes': self.stripped_value(data, KEYS.NOTES),
        }
        match step_type:
            case TYPES.RUN:
                return RunWorkoutStep(**args)
            case TYPES.RECOVER:
                return RecoverWorkoutStep(**args)
            case TYPES.REST:
                return RestWorkoutStep(**args)
            case TYPES.WARM_UP:
                return WarmUpWorkoutStep(**args)
            case TYPES.COOL_DOWN:
                return CoolDownWorkoutStep(**args)
                  
        raise InvalidStepTypeError(step_type)
    

    def stripped_value(self, data, key) -> str:
        value = data.get(key)
        if value is None:
            return None
    
        stripped = value.strip()
        if len(stripped) == 0:
            return None
        return stripped
        

    def decode_goal(self, step_type, data):
        """Decode an object corresponding to a workout goal"""
        (minimum, maximum, value) = get_limits(data)

        args = {
            'minimum': minimum,
            'maximum': maximum,
            'value': value
        }

        match step_type:
            case TYPES.SPEED:
                return SpeedGoal(**args)
            case TYPES.HEART_RATE:
                return HeartRateGoal(**args)
            case TYPES.HEART_RATE_ZONE:
                return HeartRateZoneGoal(**args)
            case TYPES.CADENCE:
                return CadenceGoal(**args)
            case TYPES.POWER:
                return PowerGoal(**args)
            case TYPES.LAP_TIME:
                return LapTimeGoal(**args)
                  
        raise InvalidGoalTypeError(step_type)
        # return f'WORKOUT GOAL: <{step_type}, {data}>'

        # if KEYS.TYPE in data:
        #     # It should be a step or a repetition...

        #     # If it has goals, lets try to decode those...

        #     goal_type = goal_type.lower()
        #     if goal_type not in STEP_GOAL_TYPES.keys():
        #         # Perform a fuzzy Levenshtein distance match to allow for a few spelling errors, etc.
        #         extracted = selectFuzzyMatch(goal_type, STEP_GOAL_TYPES.keys())
        #         if extracted is None:
        #             raise RuntimeError("Invalid goal type {}".format(goal_type))
        #         goal_type = extracted[0]
        #     self.goal_type = goal_type

        # # if 'Actor' in dct:
        # #     actor = Actor(dct['Actor']['Name'], dct['Actor']['Age'], '')
        # #     movie = Movie(dct['Movie']['Title'], dct['Movie']['Gross'], '', dct['Movie']['Year'])
        # #     return Edge(actor, movie)
        # return data
    

# # Move this to encode / decode! 
# def to_dict(self):
#     data = { KEYS.TYPE: goal_type }
#     if value is not None:
#         data[VALUE_KEY] = value
#     if min is not None:
#         data[MINIMUM_KEY] = self.min
#     if max is not None:
#         data[MAXIMUM_KEY] = self.max
#     return data
    
# @classmethod
# def from_dict(cls, data) -> Self:
#     goal_type = get_type_from_dict(data)
#     (minimum, maximum, value) = get_limits(data)
#     return WorkoutStepGoal(goal_type, value, minimum, maximum)

        
    # def from_dict(data) -> Self | None:
    #     if hasattr(data, NAME_KEY):
    #         name = data.get(name)
    #         # Process the steps
    #         steps = [from_dict(x) for x in data.get(STEPS_KEY, [])]
    #         return Workout(steps, name)
    #     if type(data) is list:
    #         # Process this as the steps...
    #         steps = [from_dict(x) for x in data]
    #         return Workout(steps)
    #     # Else see if it's a workout of some variety...
    #     if hasattr(data, KEYS.TYPE):
    #         steps = [from_dict(data)]
    #         return Workout(steps)
    #     return None