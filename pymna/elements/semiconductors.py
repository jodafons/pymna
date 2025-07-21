


__all__ = [
            "Resistor",
            "Capacitor",
            "Inductor",
            "OpAmp",
            "NoLinearResistor"
        ]

import numpy as np

from pymna import enumerator as en1um
from pymna.elements import Element
from pymna.exceptions import InvalidElement
from typing import Tuple, Union

#
# Resistor
#
class Resistor(Element):
    """
    Represents a resistor element in a circuit.

    Attributes:
    nodeIn (int): The first node connected by the resistor.
    nodeOut (int): The second node connected by the resistor.
    R (float): The resistance value of the resistor.
    """
    # This class represents a resistor element in a circuit.
    #               
    #             /\    /\    /\
    # nodeIn o---/  \  /  \  /  \  /---o nodeOut
    #                \/    \/    \/
    #
    def __init__(self, 
                 nodeIn       : int, 
                 nodeOut      : int, 
                 resistence : float, 
                 name       : str=""
            ):
        """
        Initializes an instance of the Resistor class.

        Parameters:
        nodeIn (int): The first node connected by the element.
        nodeOut (int): The second node connected by the element.
        resistence (float): The resistance value of the element.
        name (str, optional): The name of the element. Defaults to an empty string.
        """
        Element.__init__(self,name)
        self.nodeIn = nodeIn # node 1
        self.nodeOut = nodeOut # node 2
        self.R = resistence # component value

    #
    # Backward method
    #
    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
        G = (1/self.R)
        A[self.nodeIn , self.nodeIn ] +=  G
        A[self.nodeIn , self.nodeOut] += -G
        A[self.nodeOut, self.nodeIn ] += -G
        A[self.nodeOut, self.nodeOut] +=  G
        return current_branch

    def fourier(self,
                A : np.array,
                b : np.array,
                w : float,
                current_branch : int,
                ):

        G = (1/self.R)
        A[self.nodeIn , self.nodeIn ] +=  G
        A[self.nodeIn , self.nodeOut] += -G
        A[self.nodeOut, self.nodeIn ] += -G
        A[self.nodeOut, self.nodeOut] +=  G
        return current_branch    

    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, float]):
        """
        Creates a Resistor instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, int, int, float]): A tuple containing the parameters for the resistor.

        Returns:
        Resistor: An instance of the Resistor class.
        """
        if params[0][0] != "R":
            raise InvalidElement("Invalid parameters for Resistor: expected 'R' as first element.")
        return Resistor(nodeIn=int(params[1]), nodeOut=int(params[2]), resistence=float(params[3]), name=params[0])
