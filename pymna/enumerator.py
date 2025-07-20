__all__ = [
    "Method"
]


import enum 


class Method(enum.Enum):
    """
    Enumeration of methods for integration.
    """
    TRAPEZOIDAL = "trapezoidal"
    FORWARD_EULER = "forward_euler"
    BACKWARD_EULER = "backward_euler"
    