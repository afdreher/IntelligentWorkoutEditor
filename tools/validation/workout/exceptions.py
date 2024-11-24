from .constants import types as TYPES

class InvalidTypeError(ValueError):

    def __init__(self, value=None):
        if value is not None:
            super().__init__(f"Invalid type: {value}.")
        else:
            super.__init__()


class InvalidGoalTypeError(InvalidTypeError):

    def __init__(self, value=None):
        if value is not None:
            valid_types = ", ".join(TYPES.VALID_STEP_GOALS)
            super().__init__(f"Invalid type: {value}. Valid values are {valid_types}")
        else:
            super.__init__()

class InvalidStepTypeError(InvalidTypeError):

    def __init__(self, value=None):
        if value is not None:
            valid_types = ", ".join(TYPES.VALID_STEPS)
            super().__init__(f"Invalid type: {value}. Valid values are {valid_types}")
        else:
            super.__init__()