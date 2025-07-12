__all__ = [
    "Domain",
    "Integration",
    "Element"
]


import enum 


#
# tasks and jobs
#
class Domain(enum.Enum):
    TIME      = "time"
    FREQUENCY = "frequency"

class Integration(enum.Enum):
    BACKWARD_EULER = "backward"
    FORWARD_EULER  = "forward"
    TRAP_EULER     = "trap"
    GEAR           = "gear"

class Element(enum.Enum):
    RESISTOR  = "R"
    CAPACITOR = "C"
    INDUTOR   = "L"
