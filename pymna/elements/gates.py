"""
This module contains the implementation of various logic gates including NOT, AND, NAND, OR, NOR, XOR, and XNOR.
It provides functionality to calculate the output voltage and transconductance for these gates based on given inputs.

Classes:
    NOT: Represents a NOT logic gate.
    AND: Represents an AND logic gate.
    NAND: Represents a NAND logic gate.
    OR: Represents an OR logic gate.
    NOR: Represents a NOR logic gate.
    XOR: Represents an XOR logic gate.
    XNOR: Represents an XNOR logic gate.
    
Functions:
    get_G_and_V: Calculates the output voltage and transconductance for a given logic gate.

The module imports necessary types and classes from the pymna.elements package and uses NumPy for numerical operations.
"""


__all__ = ['Not',
           'AND',
           'NAND',
           'OR',
           'NOR',
           'XOR',
           'XNOR',
           ]

from typing import Tuple, List
from pymna.elements import Element
from pymna.elements import Resistor
from pymna.elements import Capacitor
from pymna.elements import CurrentSource
import numpy as np


def get_G_and_V( gate : str, 
                 V: float, 
                 A: float, 
                 ddp_a: float, 
                 ddp_b: float, 
                 control_node_a : int, 
                 control_node_b: int
                ) -> Tuple[float, float, int]:
    """
    Calculate the output voltage and transconductance for a given logic gate.

    Parameters:
    gate (str): The type of logic gate ('NOT', 'AND', 'NAND').
    V (float): The supply voltage.
    A (float): The gain factor.
    ddp_a (float): The voltage at input A.
    ddp_b (float): The voltage at input B.
    control_node_a (int): The control node index for input A.
    control_node_b (int): The control node index for input B.

    Returns:
    Tuple[float, float, int]: A tuple containing the transconductance (Go), 
                               output voltage (Vo), and the control node index.
    """
  
    VM  = V / 2
    VIH = VM + VM / A
    VIL = VM - VM / A

    if gate == "NOT":
        Vx = ddp_a  # Assuming ddp_a is the voltage at the input of the NOT gate
        control_node = control_node_a  # Assuming control_node_a is the input node for the NOT gate
        if Vx >= VIH:
            Go = 0
            Vo = 0
        if Vx <= VIH and Vx > VIL:
            Go = -A
            Vo = V/2 - Go * V/2
        if Vx <= VIL:
            Go = 0
            Vo = V
    else:

        if gate == "AND":

            if ddp_a > ddp_b:
                Vx = ddp_b
                control_node = control_node_b
            if ddp_b >= ddp_a:
                Vx = ddp_a
                control_node = control_node_a

            if Vx > VIH:
                Go = 0
                Vo = V 
            if Vx <= VIH and Vx > VIL:
                Go = A
                Vo = V/2 - Go * V/2
            if Vx <= VIL:
                Go = 0
                Vo = 0

        elif gate == "NAND":

            if ddp_a > ddp_b:
                Vx = ddp_b
                control_node = control_node_b
            if ddp_b >= ddp_a:
                Vx = ddp_a
                control_node = control_node_a
       
            if Vx > VIH:
                Go = 0
                Vo = V 
            if Vx <= VIH and Vx > VIL:
                Go = -A
                Vo = V/2 - Go * V/2
            if Vx <= VIL:
                Go = 0
                Vo = V
        elif gate == "OR":

            if ddp_a > ddp_b:
                Vx = ddp_b
                control_node = control_node_b
            if ddp_b >= ddp_a
                Vx = ddp_a
                control_node = control_node_a

            if Vx > VIH:
                Go = 0
                Vo = V 
            if Vx <= VIH and Vx > VIL:
                Go = A
                Vo = V/2 - Go * V/2
            if Vx <= VIL:
                Go = 0
                Vo
        elif gate == "NOR":

            if ddp_a > ddp_b:
                Vx = ddp_a
                control_node = control_node_a
            if ddp_b >= ddp_a
                Vx = ddp_b
                control_node = control_node_b

            if Vx > VIH:
                Go = 0
                Vo = 0
            if Vx <= VIH and Vx > VIL:
                Go = -A
                Vo = V/2 - Go * V/2
            if Vx <= VIL:
                Go = 0
                Vo = V

        elif gate == "XOR":

            # VA >= VB and VA + VB > V
            if ddp_a >= ddp_b and (ddp_a + ddp_b) > V:
                Vx = ddp_b
                control_node = control_node_b
                V_partOne = V
                derived_partTwo = -A
                V_partThree = 0

            # VB > VA and VA + VB > V
            if ddp_b > ddp_a and (ddp_a + ddp_b) > V:
                Vx = ddp_a
                control_node = control_node_a
                V_partOne = V
                derived_partTwo = -A
                V_partThree = 0
							
			# VA >= VB e VA + VB < V
            if ((ddp_a >= ddp_b) and ((ddp_a + ddp_b) < V)):
                Vx = ddp_a
                control_node = control_node_a
                V_partOne = 0
                derived_partTwo = A
                V_partThree = V
							
			# VB > VA e VA + VB < V
            if ((ddp_b > ddp_a) and ((ddp_a + ddp_b) < V)):
                Vx = ddp_b
                control_node = control_node_b
                V_partOne = 0
                derived_partTwo = A
                V_partThree = V
	
			if Vx > VIH:
                Go = 0
                Vo = V_partThree
            if Vx <= VIH and Vx > VIL:
                Go = derived_partTwo
                Vo = V/2 - Go * V/2
            if Vx <= VIL:
                Go = 0
                Vo = V_partOne
								
						
        elif gate == "XNOR":

            # VA >= VB e VA + VB > V
            if (ddp_a >= ddp_b) and ((ddp_a + ddp_b) > V):
                Vx = ddp_b
                control_node = control_node_b
                V_partOne = 0
                derived_partTwo = A
                V_partThree = V

            # VB > VA e VA + VB > V
            if (ddp_b > ddp_a) and ((ddp_a + ddp_b) > V):
                Vx = ddp_a
                control_node = control_node_a
                V_partOne = 0
                derived_partTwo = A
                V_partThree = V
	
							
			# VA >= VB e VA + VB < V
            if ((ddp_a >= ddp_b) and ((ddp_a + ddp_b) < V)):
                Vx = ddp_a
                control_node = control_node_a
                V_partOne = V
                derived_partTwo = -A
                V_partThree = 0

            # VB > VA e VA + VB < V
            if ((ddp_b > ddp_a) and ((ddp_a + ddp_b) < V)):
                Vx = ddp_b
                control_node = control_node_b
                V_partOne = V
                derived_partTwo = -A
                V_partThree = 0

							
					
            if Vx > VIH:
                Go = 0
                Vo = V_partThree
			if (Vx <= VIH) and (Vx > VIL):
                Go = derived_partTwo
                Vo = V/2 - Go * V/2
            if (Vx <= VIL):
                Go = 0
                Vo = V_partOne

        else:
            raise ValueError(f"Unknown gate type: {gate}")

    return Go, Vo, control_node



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
            Initializes a gate element with specified parameters.

            Parameters:
            nodeIn (int): The input node of the gate.
            nodeOut (int): The output node of the gate.
            V (float): The voltage associated with the gate.
            C (float): The capacitance value of the gate.
            A (float): The area of the gate.
            R (float): The resistance value of the gate.
            name (str, optional): The name of the gate element. Defaults to an empty string.

            This constructor initializes the gate element with the provided parameters
            and sets the ground and initial current values.
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

        # get G and V given the gate type and inputs
        Go, Vo, control_node = get_G_and_V("NOT", self.V, self.A, ddp, 0, self.control_nodeIn, o)

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
        
        # get G and V given the gate type and inputs
        Go, Vo, control_node = get_G_and_V(self.gate_name, self.V, self.A, ddp_a, ddp_b, self.control_nodeIn_a, self.control_nodeIn_b)

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
            """
            Initializes an AND gate with the specified parameters.

            Parameters:
            nodeIn_a (int): The first input node.
            nodeIn_b (int): The second input node.
            nodeOut (int): The output node.
            V (float): The voltage.
            C (float): The capacitance.
            A (float): The area.
            R (float): The resistance.
            name (str, optional): The name of the gate. Defaults to an empty string.

            This constructor calls the parent class (TwoInputsGate) 
            initializer with the specified parameters and sets the gate type to "AND".
            """
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
            """
            Initializes a NAND gate with the specified parameters.

            Parameters:
            nodeIn_a (int): The first input node.
            nodeIn_b (int): The second input node.
            nodeOut (int): The output node.
            V (float): The voltage.
            C (float): The capacitance.
            A (float): The area.
            R (float): The resistance.
            name (str, optional): The name of the gate. Defaults to an empty string.

            This constructor calls the parent class (TwoInputsGate) constructor
            with the specified parameters and sets the gate type to "NAND".
            """
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
            """
            Initializes an OR gate with the specified parameters.

            Parameters:
            nodeIn_a (int): The first input node.
            nodeIn_b (int): The second input node.
            nodeOut (int): The output node.
            V (float): The voltage.
            C (float): The capacitance.
            A (float): The area.
            R (float): The resistance.
            name (str, optional): The name of the gate. Defaults to an empty string.

            This constructor calls the parent class (TwoInputsGate) initializer
            with the specified parameters and sets the gate type to "OR".
            """
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
            """
            Initializes a NOR gate with the specified parameters.

            Parameters:
            nodeIn_a (int): The first input node.
            nodeIn_b (int): The second input node.
            nodeOut (int): The output node.
            V (float): The voltage.
            C (float): The capacitance.
            A (float): The area.
            R (float): The resistance.
            name (str, optional): The name of the gate. Defaults to an empty string.

            This constructor calls the parent class (TwoInputsGate) constructor
            with the specified parameters and sets the gate type to "NOR".
            """
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
            """
            Initializes a two-input XOR gate with the specified parameters.

            Parameters:
            nodeIn_a (int): The first input node.
            nodeIn_b (int): The second input node.
            nodeOut (int): The output node.
            V (float): The voltage.
            C (float): The capacitance.
            A (float): The area.
            R (float): The resistance.
            name (str, optional): The name of the gate. Defaults to an empty string.

            Inherits from TwoInputsGate and initializes it with the type "XOR".
            """
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
            """
            Initializes an XNOR gate with the specified parameters.

            Parameters:
            nodeIn_a (int): The first input node.
            nodeIn_b (int): The second input node.
            nodeOut (int): The output node.
            V (float): The voltage.
            C (float): The capacitance.
            A (float): The area.
            R (float): The resistance.
            name (str, optional): The name of the gate. Defaults to an empty string.

            Inherits from TwoInputsGate and initializes it with the type "XNOR".
            """
            TwoInputsGate.__init__(self, nodeIn_a, nodeIn_b, nodeOut, V, C, A, R, "XNOR", name)
