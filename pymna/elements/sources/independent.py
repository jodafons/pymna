
__all__ = [
    "VoltageSource",
    "CurrentSource",
]

import numpy as np

from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC

class VoltageSource(Source):
    def __init__(self, 
                 nodeIn  : int,
                 nodeOut : int,
                 V       : float=0,
                 name    : str=""
            ):
        """
        Initializes a DCVoltageSource object with the given parameters.
        This class represents a DC voltage source in a circuit simulation.

        Parameters:
            nodeIn (int): The input node of the source.
            nodeOut (int): The output node of the source.
            dc (float, optional): The DC voltage value. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.
        """
        Source.__init__(self, name, nodeIn, nodeOut)
        self.V = V

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:

        A[self.nodeIn,self.jx]   +=  1
        A[self.nodeOut,self.jx]  += -1
        A[self.jx, self.nodeIn]  += -1
        A[self.jx, self.nodeOut] +=  1
        b[self.jx] += -self.V
        return current_branch

class CurrentSource(Source):
    def __init__(self, 
                 nodeIn  : int,
                 nodeOut : int,
                 I       : float=0,
                 name    : str=""
            ):
        """
        Initializes a DCCurrentSource object with the given parameters.
        This class represents a DC current source in a circuit simulation.

        Parameters:
            nodeIn (int): The input node of the source.
            nodeOut (int): The output node of the source.
            dc (float, optional): The DC current value. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.
        """
        Source.__init__(self, name, nodeIn, nodeOut)
        self.I = I

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
        I = self.I
        b[self.nodeIn]   += -I
        b[self.nodeOut]  +=  I
        return current_branch
