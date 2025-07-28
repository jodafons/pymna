__all__ = [
            "OpAmp",
        ]

import numpy as np
from pymna.elements import Element
from pymna.exceptions import InvalidElement
from typing import Tuple, Union


#
# OpAmp
#
class OpAmp(Element):

    # This class represents an operational amplifier element in a circuit.
    # The letter is 'O'.
    def __init__(self, 
                 controlNodePos : int,
                 controlNodeNeg : int,
                 nodeOut        : int,
                 name           : str=""
    ):
        """
        Initializes an instance of the Ampop class.

        Parameters:
        controlNodePos (int): The positive control node of the operational amplifier.
        controlNodeNeg (int): The negative control node of the operational amplifier.
        nodeOut (int): The positive output node of the operational amplifier.
        name (str, optional): The name of the operational amplifier. Defaults to an empty string.
        """
        Element.__init__(self, name)
        self.controlNodePos = controlNodePos
        self.controlNodeNeg = controlNodeNeg
        self.nodeOutPos     = nodeOut
        self.nodeOutNeg     = 0

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
 
        current_branch += 1
        jx = current_branch
        A[self.nodeOutPos, jx]     +=  1 
        A[self.nodeOutNeg, jx]     += -1
        A[jx, self.controlNodePos] += -1
        A[jx, self.controlNodeNeg] +=  1
        return current_branch

    def fourier(                self,
                A : np.array,
                b : np.array,
                w : float,
                current_branch : int,
                ):
        current_branch += 1
        jx = current_branch
        A[self.nodeOutPos, jx]     +=  1 
        A[self.nodeOutNeg, jx]     += -1
        A[jx, self.controlNodePos] += -1
        A[jx, self.controlNodeNeg] +=  1
        return current_branch

    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, int]):
        """
        Creates an Ampop instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, int, int, int]): A tuple containing the parameters for the operational amplifier.

        Returns:
        Ampop: An instance of the Ampop class.
        """
        if params[0][0] != "O":
            raise InvalidElement("Invalid parameters for Operational Amplifier: expected 'O' as first element.")
        return Ampop(controlNodePos=int(params[1]), controlNodeNeg=int(params[2]), nodeOut=int(params[3]), name=params[0])
