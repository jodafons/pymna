

__all__ = [
            "Element",
        ]

from typing import Tuple
from abc import ABC, abstractmethod

class Element(ABC):
    def __init__(self, name : str):
        self.name=name

    #@abstractmethod
    #def backward(self, A, b, delta_t : float, current_branch : int) -> int:
    #    return -1

    #@abstractmethod
    #def trap(self, A, b):
    #    pass

    #@abstractmethod
    #def update(self, x):
    #    pass

    #@abstractmethod
    #def fourier(self):
    #    pass