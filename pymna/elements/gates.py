__all__ = ['Not']

from typing import Tuple, List
from pymna.elements import Element
from pymna.elements import Resistor
from pymna.elements import Capacitor
from pymna.elements import DCCurrentSource, CurrentSourceControlByVoltage
import numpy as np


def get_G_and_V( gate : str, Vx : float, V: float, A: float) -> Tuple[float, float]:

    VM  = V / 2
    VIH = VM + VM / A
    VIL = VM - VM / A

    if gate == "NOT":
        if Vx >= VIH:
            Go = 0
            Vo = 0
        elif Vx <= VIH and Vx > VIL:
            Go = -A
            Vo = V/2 - G * V/2
        elif Vx <= VIL:
            Go = 0
            Vo = V
    elif gate == "AND":
        if Vx > VIH:
            Go = 0
            Vo = V 
        elif Vx <= VIH and Vx > VIL:
            Go = A
            Vo = V/2 - G * V/2
        elif Vx <= VIL:
            Go = 0
            Vo = 0
    elif gate == "NAND":
        if Vx > VIH:
            Go = 0
            Vo = V 
        elif Vx <= VIH and Vx > VIL:
            Go = -A
            Vo = V/2 - G * V/2
        elif Vx <= VIL:
            Go = 0
            Vo = V
    elif gate == "OR":
        if Vx > VIH:
            Go = 0
            Vo = V 
        elif Vx <= VIH and Vx > VIL:
            Go = A
            Vo = V/2 - G * V/2
        elif Vx <= VIL:
            Go = 0
            Vo
    elif gate == "NOR":


    elif gate == "XOR":


    elif gate == "XNOR":


    else:
        raise ValueError(f"Unknown gate type: {gate}")

    return Go, Vo



class NOT(Element):

    def __init__(self, 
                     nodeIn  : int, 
                     nodeOut : int, 
                     V       : float,
                     C       : float,
                     A       : float,
                     R       : float,
                     name    : str = ""
                     ):
            """
            Initializes a new instance of the class.

            Parameters:
            nodeIn (int): The input node identifier.
            nodeOut (int): The output node identifier.
            V (float): The voltage associated with the element.
            C (float): The capacitance value of the element.
            A (float): The area associated with the element.
            R (float): The resistance value of the element.
            name (str, optional): The name of the element. Defaults to an empty string.

            Attributes:
            control_nodeIn (int): The input node identifier.
            nodeOut (int): The output node identifier.
            R (float): The resistance value of the element.
            V (float): The voltage associated with the element.
            C (float): The capacitance value of the element.
            A (float): The area associated with the element.
            gnd (int): Ground reference, initialized to 0.
            ic_a (int): Initial condition for the element, initialized to 0.
            """
            Element.__init__(self, name)
            self.control_nodeIn = nodeIn
            self.nodeOut        = nodeOut
            self.R              = R 
            self.V              = V 
            self.C              = C 
            self.A              = A
            self.gnd            = 0
            self.ic_a           = 0

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
        
        ddp = x_newton_raphson[self.control_nodeIn] - x_newton_raphson[self.gnd]
        control_node = self.control_nodeIn

        # input A
        # Capacitor from control_nodeIn to gnd in parallel with 
        # a current source from gnd to control_nodeIn (initial condition)
        Ca = Capacitor( self.control_nodeIn, self.gnd, self.C, ic = self.ic_a )
        current_branch = Ca.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

        Go, Vo = get_G_and_V("NOT", ddp, self.V, self.A)

        # output
        A[self.gnd, control_node ]    +=  Go  # G
        A[self.gnd, self.gnd]         += -Go  # G
        A[self.nodeOut, control_node] += -Go  # G
        A[self.nodeOut, self.gnd]     +=  Go  # G

        # current source from nodeOut to gnd 
        Iout = CurrentSource( self.gnd, self.nodeOut,  Vo/self.R )   
        current_branch = Iout.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

        # resistor from nodeOut to gnd
        Rout  = Resistor( self.nodeOut, self.gnd, self.R )
        current_branch = Rout.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

        # backward pass
        return current_branch			
				
    def update(self, x : np.array)
        self.ic_a = x[self.control_nodeIn] - x[self.gnd]

class TwoInputsGate(Element):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     gate_name : str,
                     name      : str = ""
                     ):
 
            Element.__init__(self, name)
            self.control_nodeIn_a = nodeIn_a
            self.control_nodeIn_b = nodeIn_b
            self.nodeOut          = nodeOut
            self.R                = R 
            self.V                = V 
            self.C                = C 
            self.A                = A
            self.gnd              = 0
            self.ic_a             = 0
            self.ic_b             = 0
            self.gate_name        = gate_name

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
        
        ddp_a = x_newton_raphson[self.control_nodeIn_a] - x_newton_raphson[self.gnd]
        ddp_b = x_newton_raphson[self.control_nodeIn_b] - x_newton_raphson[self.gnd]

        # input A
        Ca = Capacitor( self.control_nodeIn_a, self.gnd, self.C, ic = self.ic_a )
        current_branch = Ca.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

        # input B
        Cb = Capacitor( self.control_nodeIn_b, self.gnd, self.C, ic = self.ic_b )
        current_branch = Cb.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        
        if ddp_a > ddp_b:
            Vx = ddp_b
            control_node = self.control_nodeIn_b
        if ddp_b >= ddp_a
            Vx = ddp_a
            control_node = self.control_nodeIn_a

        Go, Vo = get_G_and_V(self.gate_name, Vx, self.V, self.A)

        # output
        A[self.gnd, control_node ]    +=  Go  # G
        A[self.gnd, self.gnd]         += -Go  # G
        A[self.nodeOut, control_node] += -Go  # G
        A[self.nodeOut, self.gnd]     +=  Go  # G

        # current source from nodeOut to gnd 
        Iout = CurrentSource( self.gnd, self.nodeOut,  Vo/self.R )   
        current_branch = Iout.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

        # resistor from nodeOut to gnd
        Rout  = Resistor( self.nodeOut, self.gnd, self.R )
        current_branch = Rout.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

        # backward pass
        return current_branch			
				
    def update(self, x : np.array)
        self.ic_a = x[self.control_nodeIn] - x[self.gnd]
        self.ic_b = x[self.control_nodeIn_b] - x[self.gnd]



class AND(TwoInputsGate):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     name      : str = ""
                     ):
 
        TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "AND", name)

class NAND(TwoInputsGate):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     name      : str = ""
                     ):
 
        TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "NAND", name)

class OR(TwoInputsGate):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     name      : str = ""
                     ):
 
        TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "OR", name)

class NOR(TwoInputsGate):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     name      : str = ""
                     ):
 
        TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "NOR", name)

class XOR(TwoInputsGate):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     name      : str = ""
                     ):
 
        TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "XOR", name)

class XNOR(TwoInputsGate):

    def __init__(self, 
                     nodeIn_a  : int, 
                     nodeIn_b  : int,
                     nodeOut   : int, 
                     V         : float,
                     C         : float,
                     A         : float,
                     R         : float,
                     name      : str = ""
                     ):
 
        TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "XNOR", name)
