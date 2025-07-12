

__all__ = [
            "Element",
        ]

from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC

class Element(ABC):
    def __init__(self):

    @abstractmethod
    def backward(self, A, b)
        pass

    @abstractmethod
    def trap(self, A, b):
        pass

    @abstractmethod
    def update(self, x):
        pass

    @abstractmethod
    def fourier(self):
        pass