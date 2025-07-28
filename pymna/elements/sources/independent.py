
__all__ = [
    "VoltageSource",
    "CurrentSource",
]

import numpy as np
from pymna.elements import Element, Step
from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC

class VoltageSource(Element):
    
    def __init__(self, 
                 nodeIn  : int,
                 nodeOut : int,
                 V       : float=0,
                 name    : str=""
            ):
        """
        Initializes a VoltageSource object with the given parameters.
        This class represents a DC voltage source in a circuit simulation.

        Parameters:
            nodeIn (int): The input node of the source.
            nodeOut (int): The output node of the source.
            dc (float, optional): The DC voltage value. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.
        """
        Element.__init__(self, name)
        self.nodeIn  = nodeIn
        self.nodeOut = nodeOut        
        self.V = V

    def backward(self, 
                 step              : Step,
                 ):
        step.current_branch += 1
        jx = step.current_branch
        step.A[self.nodeIn,jx]   +=  1
        step.A[self.nodeOut,jx]  += -1
        step.A[jx, self.nodeIn]  += -1
        step.A[jx, self.nodeOut] +=  1
        step.b[jx] += -self.V
        
class CurrentSource(Element):
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
        Element.__init__(self, name)
        self.nodeIn  = nodeIn
        self.nodeOut = nodeOut
        self.I = I

    def backward(self, 
                 step              : Step,
                 ):
        I = self.I
        step.b[self.nodeIn]   += -I
        step.b[self.nodeOut]  +=  I
        