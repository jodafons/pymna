__all__ = ['Not']

from typing import Tuple, List
from pymna.elements import Element
from pymna.elements import Resistor
from pymna.elements import Capacitor
from pymna.elements import DCCurrentSource, CurrentSourceControlByVoltage
import numpy as np


class Not(Element):

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
            self.nodeOut = nodeOut
            self.R = R 
            self.V = V 
            self.C = C 
            self.A = A
            self.gnd = 0
            self.ic_a = 0

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

        # input A
        Ca = Capacitor( self.control_nodeIn, self.gnd, self.C )
        Ia = DCCurrentSource( self.gnd, self.control_nodeIn, self.C (self.ic_a/dt) )
        
        VM  = self.V / 2
        VIH = VM + VM / self.A
        VIL = VM - VM / self.A

        if ddp >= VIH:
            V = 0
            G = 0
        elif ddp <= VIH and ddp > VIL:
            G = -self.A
            V = -self.V/2 + G * self.V/2
        elif ddp <= VIL:
            G = 0
            V = self.V

        # output
        I1out = CurrentSourceControlByVoltage( self.nodeOut, self.gnd, self.control_nodeIn, self.gnd, G/self.R )
        I2out = DCCurrentSource( self.nodeOut, self.gnd, V/self.R )
        Rout  = Resistor( self.nodeOut, self.gnd, self.R )

        # backward pass
        current_branch = Ca.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = Ia.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = I1out.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = I2out.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = Rout.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        return current_branch			
				
    def update(self, x : np.array)
        self.ic_a = x[self.control_nodeIn] - x[self.gnd]


class And(Element):

    def __init__(self, 
                     nodeIn_a : int, 
                     nodeIn_b : int, 
                     nodeOut  : int, 
                     V        : float,
                     C        : float,
                     A        : float,
                     R        : float,
                     name     : str = ""
                     ):
        """
        Initializes a new instance of the class.

        Parameters:
        nodeIn_a (int): The first input node identifier.
        nodeIn_b (int): The second input node identifier.
        nodeOut (int): The output node identifier.
        V (float): The voltage associated with the element.
        C (float): The capacitance value of the element.
        A (float): The area associated with the element.
        R (float): The resistance value of the element.
        name (str, optional): The name of the element. Defaults to an empty string.

        Attributes:
        control_nodeIn_a (int): The first input node identifier.
        control_nodeIn_b (int): The second input node identifier.
        nodeOut (int): The output node identifier.
        R (float): The resistance value of the element.
        V (float): The voltage associated with the element.
        C (float): The capacitance value of the element.
        A (float): The area associated with the element.
        gnd (int): Ground reference, initialized to 0.
        ic_a1 (int): Initial condition for the first input, initialized to 0.
        ic_a2 (int): Initial condition for the second input, initialized to 0.
        """
        Element.__init__(self, name)
        self.control_nodeIn_a = nodeIn_a
        self.control_nodeIn_b = nodeIn_b
        self.nodeOut = nodeOut
        self.R = R 
        self.V = V 
        self.C = C 
        self.A = A
        self.gnd = 0
        self.ic_a1 = 0
        self.ic_a2 = 0

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
        Ca1 = Capacitor( self.control_nodeIn_a, self.gnd, self.C )
        Ia1 = DCCurrentSource( self.gnd, self.control_nodeIn_a, self.C (self.ic_a1/dt) )

        # input B
        Ca2 = Capacitor( self.control_nodeIn_b, self.gnd, self.C )
        Ia2 = DCCurrentSource( self.gnd, self.control_nodeIn_b, self.C (self.ic_a2/dt) )
        
        VM  = self.V / 2
        VIH = VM + VM / self.A
        VIL = VM - VM / self.A

        if ddp_a >= VIH and ddp_b >= VIH:
            V = 0
            G = 0
        elif (ddp_a >= VIH and ddp_b <= VIH and ddp_b > VIL) or (ddp_b >= VIH and ddp_a <= VIH and ddp_a > VIL):
            G = -self.A
            V = -self.V/2 + G * self.V/2
        elif ddp_a <= VIL and ddp_b <= VIL:
            G = 0
            V = self.V

        # output
        Gout = G/self.Rout
        I1out = CurrentSourceControlByVoltage( self.nodeOut, self.gnd, self.control_nodeIn_a, self.gnd, G/self.Rout )
        I2out = DCCurrentSource( self.nodeOut, self.gnd, V/self.Rout )
        Rout  = Resistor( self.nodeOut, self.gnd, self.Rout )

        # backward pass
        current_branch = Ca1.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = Ia1.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = Ca2.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = Ia2.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = I1out.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        current_branch = I2out.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        return current_branch


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