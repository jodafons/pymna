__all__ = [
            "IdealOpAmp",
            "OpAmp"
        ]

import numpy as np
from pymna.elements import Element, Step
from pymna.elements.basics import Resistor, Capacitor 
from pymna.elements.sources.dependent import VoltageSourceControlByVoltage
from pymna.exceptions import InvalidElement
from typing import Tuple, Union


#
# OpAmp
#
class IdealOpAmp(Element):

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
                 step : Step,
                 ):
 
        step.current_branch += 1
        jx = step.current_branch
        step.A[self.nodeOutPos, jx]     +=  1 
        step.A[self.nodeOutNeg, jx]     += -1
        step.A[jx, self.controlNodePos] += -1
        step.A[jx, self.controlNodeNeg] +=  1
        
    def fourier(self,
                step : Step,
                ):
        step.current_branch += 1
        jx = step.current_branch
        step.A[self.nodeOutPos, jx]     +=  1 
        step.A[self.nodeOutNeg, jx]     += -1
        step.A[jx, self.controlNodePos] += -1
        step.A[jx, self.controlNodeNeg] +=  1
        
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


class OpAmp(Element):

    # This class represents an operational amplifier element in a circuit.
    # The letter is 'O'.
    def __init__(self, 
                 controlNodePos : int,
                 controlNodeNeg : int,
                 nodeOut        : int,
                 Rin            : Union[float, int]=2e6,  # Input resistance
                 Rout           : Union[float, int]=75,   # Output resistance
                 A              : Union[float, int]=1e5,  # Gain
                 C              : Union[float, int]=3e-9, # Capacitance
                 name           : str=""
    ):
        """
        Initializes an instance of the Ampop class.

        Parameters:
        controlNodePos (int): The positive control node of the operational amplifier.
        controlNodeNeg (int): The negative control node of the operational amplifier.
        nodeOut (int): The positive output node of the operational amplifier.
        nodeSource (int): The source node of the operational amplifier (auxiliar node).
        name (str, optional): The name of the operational amplifier. Defaults to an empty string.
        """
        Element.__init__(self, name)
        self.controlNodePos = controlNodePos
        self.controlNodeNeg = controlNodeNeg
        self.nodeOutPos     = nodeOut
        self.nodeOutNeg     = 0 # ground
        self.Rin            = Rin
        self.Rout           = Rout
        self.Av             = A
        self.C              = C
 
    def backward(self, 
                 step : Step,
                 ):
        
        step.current_branch += 1
        vx = step.current_branch
        Rin = Resistor( self.controlNodePos, self.controlNodeNeg, self.Rin )
        Rin.backward(step)
        A = VoltageSourceControlByVoltage( vx, self.nodeOutNeg, self.controlNodePos, self.controlNodeNeg, self.Av )
        A.backward(step)
        Rout = Resistor( vx, self.nodeOutPos, self.Rout )
        Rout.backward(step)
        C = Capacitor( self.nodeOutPos, self.nodeOutNeg, self.C)
        C.backward(step)

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
        return OpAmp(controlNodePos=int(params[1]), controlNodeNeg=int(params[2]), nodeOut=int(params[3]), name=params[0])

