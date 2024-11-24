from typing import Self
import uuid


class WorkoutObject(object):
    """
    This is the base class for all workout objects: steps, goals, etc.
    """

    def __init__(self):
        self.uuid = uuid.uuid4().hex.upper()

    # Override this to provide some customization.
    def to_str(self, depth: int = 0) -> str:
        return f"WorkoutObject <{self.uuid}>"

    def __repr__(self) -> str:
        return self.to_str()
          
    def __str__(self) -> str:
        return self.to_str()
    
    def similar(self: Self, other: Self | None) -> bool:
        if other is None:
            return False

        return type(self) is type(other)
    
    def compressed(self) -> Self | None:
        return self