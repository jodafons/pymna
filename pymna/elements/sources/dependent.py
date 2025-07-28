
__all__ = [
    "VoltageSourceControlByVoltage",
    "CurrentSourceControlByCurrent",
    "CurrentSourceControlByVoltage",
    "VoltageSourceControlByCurrent",

]

import numpy as np
from pymna.elements import Element, Step
from pymna.elements.element import condutance, transcondutance
from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC

#
# Voltage and current source gains
#

class VoltageSourceControlByVoltage(Element):

    # This class represents a voltage source controlled by another voltage source.
    # The letter is 'E'.
    def __init__(self, 
                 nodeIn          : int,
                 nodeOut         : int,
                 controlNodeIn   : int,
                 controlNodeOut  : int,
                 Av              : float,
                 name            : str=""
            ):
        """
        Initializes a Source object.

        Parameters:
        nodeIn (int): The input node identifier.
        nodeOut (int): The output node identifier.
        Av (float): The voltage gain.
        name (str, optional): The name of the source. Defaults to an empty string.

        This constructor calls the parent class's __init__ method to initialize
        the node identifiers and sets the voltage gain.
        """
        
        Source.__init__(self, name, nodeIn, nodeOut)
        self.Av = Av
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

    def backward(self, 
                 step : Step
                 ):

        step.current_branch += 1
        jx = step.current_branch
        step.A[self.nodeIn , jx]        +=  1
        step.A[self.nodeOut , jx]       += -1
        step.A[jx, self.nodeIn]         += -1
        step.A[jx, self.nodeOut]        +=  1
        step.A[jx, self.controlNodeIn]  += self.Av
        step.A[jx, self.controlNodeOut] += -self.Av 

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # VoltageSourceControlByVoltage: 'E'name, noIn, noOut, control_noIn, control_noOut, Av
        if params[0][0] != 'E' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for VoltageSourceControlByVoltage: expected 'E'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return VoltageSourceControlByVoltage( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Av=float(params[5]),
                                              name=params[0])
 
class CurrentSourceControlByCurrent(Element):
   
   # This class represents a current source controlled by a voltage source.
   # The letter if 'F'
    def __init__(self, 
             nodeIn         : int,
             nodeOut        : int,
             controlNodeIn  : int,
             controlNodeOut : int,
             Ai             : float,
             name           : str=""
            ):
        """
        Initializes a Source object.

        Parameters:
        nodeIn (int): The input node identifier.
        nodeOut (int): The output node identifier.
        Ai (float): The current gain.
        name (str, optional): The name of the source. Defaults to an empty string.
        
        Calls the parent class's __init__ method to initialize the node identifiers.
        """
        Element.__init__(self, name)
        self.nodeIn  = nodeIn
        self.nodeOut = nodeOut
        self.Ai = Ai
        self.controlNodeIn  = controlNodeIn
        self.controlNodeOut = controlNodeOut

    def backward(self, 
                 step : Step
                 ):

        step.current_branch += 1
        jx = step.current_branch
        step.A[self.controlNodeIn , jx]   +=  1
        step.A[self.controlNodeOut, jx]   += -1
        step.A[jx, self.controlNodeIn]    += -1
        step.A[jx, self.controlNodeOut]   +=  1
        step.A[self.nodeIn , jx]          +=  self.Ai
        step.A[self.nodeOut , jx]         += -self.Ai

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # CurrentSourceControlByVoltage: 'F'name, noIn, noOut, control_noIn, control_noOut, Ai
        if params[0][0] != 'F' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for CurrentSourceControlByCurrent expected 'F'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return CurrentSourceControlByCurrent( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Ai=float(params[5]),
                                              name=params[0])

# Trancondutance
class CurrentSourceControlByVoltage(Element):
    
    # This class represents a current source controlled by a voltage source.
    # The letter is 'G'.
    def __init__(self, 
             nodeIn  : int,
             nodeOut : int,
             controlNodeIn  : int,
             controlNodeOut : int,
             Gm       : float,
             name     : str=""
            ):
        """
        Initializes a Source object with the given parameters.

        Parameters:
        nodeIn (int): The input node of the source.
        nodeOut (int): The output node of the source.
        controlNodeIn (int): The control input node for the source.
        controlNodeOut (int): The control output node for the source.
        Gm (float): Transconductance gain of the source.
        name (str, optional): The name of the source. Defaults to an empty string.

        """
        Element.__init__(self, name)
        self.nodeIn  = nodeIn
        self.nodeOut = nodeOut        
        self.Gm = Gm
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

    def backward(self, 
                 step : Step
                 ):

        transcondutance(step.A, self.nodeIn, self.nodeOut, self.controlNodeIn, self.controlNodeOut, self.Gm)

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # CurrentSourceControlByVoltage: 'G'name, noIn, noOut, control_noIn, control_noOut, Gm
        if params[0] != 'G' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for CurrentSourceControlByVoltage: expected 'G'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return CurrentSourceControlByVoltage( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Gm=float(params[5]),
                                              name=params[0])

class VoltageSourceControlByCurrent(Element):

    # This class represents a voltage source controlled by a current source.
    # The letter is 'H'.
    def __init__(self, 
                 nodeIn         : int,
                 nodeOut        : int,
                 controlNodeIn  : int,
                 controlNodeOut : int,
                 Rm             : float,
                 name           : str=""
            ):
        """
     
        """
        
        Element.__init__(self, name)
        self.nodeIn  = nodeIn
        self.nodeOut = nodeOut        
        self.Rm = Rm
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

    def backward(self, 
                 step : Step
                 ):

        step.current_branch += 1
        # current main branch
        jx = step.current_branch
        step.current_branch += 1
        # current control branch
        jy = step.current_branch

        step.A[self.nodeIn  , jx       ] +=  1 # I
        step.A[self.nodeOut , jx       ] += -1 # I
        step.A[self.controlNodeIn  , jy] +=  1 # I
        step.A[self.controlNodeOut, jy ] += -1 # I
        step.A[jx, self.controlNodeIn  ] += -1 # V
        step.A[jx, self.controlNodeOut ] +=  1 # V
        step.A[jy, self.controlNodeIn  ] += -1 # V
        step.A[jy, self.controlNodeOut ] +=  1 # V
        step.A[jx,jy]                    += self.Rm
        
    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # VoltageSourceControlByCurrent: 'H'name, noIn, noOut, control_noIn, control_noOut, Rm
        if params[0][0] != 'H' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for VoltageSourceControlByCurrent: expected 'H'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return VoltageSourceControlByCurrent( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Rm=float(params[5]),
                                              name=params[0])