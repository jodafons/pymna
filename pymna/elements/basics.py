

"""
This module defines basic electrical elements including Resistor, Capacitor, and Inductor.
These elements are subclasses of the Element class and implement methods for simulating
their behavior in electrical circuits.

Classes:
    - Resistor: Represents a resistor element in a circuit.
    - Capacitor: Represents a capacitor element in a circuit.
    - Indutor: Represents an inductor element in a circuit.

Each class includes methods for initializing the element, performing backward analysis,
and updating initial conditions.
"""




__all__ = [
            "Resistor",
            "Capacitor",
            "Indutor",
        ]

import numpy as np

from pymna import enumerator as en1um
from pymna.elements import Element
from pymna.exceptions import InvalidElement
from typing import Tuple



#
# Resistor
#
class Resistor(Element):

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
        Initializes an instance of the Element class.

        Parameters:
        a (int): The first node connected by the element.
        b (int): The second node connected by the element.
        resistence (float): The resistance value of the element.
        name (str, optional): The name of the element. Defaults to an empty string.

        """
        Element.__init__(self,name)
        self.nodeIn = nodeIn # node 1
        self.nodeOut = nodeOut # node 2
        self.R = resistence # component value


    #
    # Backward method
    def backward(self, 
                 A : np.array, 
                 b : np.array, 
                 t : float,
                 deltaT : float,
                 current_branch : int, 
                 ):
        G = (1/self.R)
        A[self.nodeIn , self.nodeIn ] +=  G
        A[self.nodeIn , self.nodeOut] += -G
        A[self.nodeOut, self.nodeIn ] += -G
        A[self.nodeOut, self.nodeOut] +=  G
        return current_branch


    @classmethod
    def from_nl( cls, params : Tuple[str, str, int, int, float] ) -> Resistor:
        # Resistor: 'R', name, nodeIn, nodeOut, resistance
        if params[0]!="R":
            raise InvalidElement("Invalid parameters for Resistor: expected 'R' as first element.")
        return Resistor(nodeIn=params[2], nodeOut=params[3], resistence=params[4], name=params[1])



#
# Capacitor
#
class Capacitor(Element):
    #
    #          | |
    #          | |
    #  a o-----| |-----o b
    #          | |
    #          | |
    #
    def __init__(self,
             nodeIn             : int,
             nodeOut            : int,
             capacitance        : float,
             initial_condition  : float=0,
             name               : str=""
            ):
        """
        Initializes a new instance of the Element class.

        Parameters:
        a (int): The first node connected to the element (node 1).
        b (int): The second node connected to the element (node 2).
        capacitance (float): The capacitance value of the element.
        initial_condition (float, optional): The initial condition of the element. Defaults to 0.
        name (str, optional): The name of the element. Defaults to an empty string.

        """
        Element.__init__(self,name)
        self.nodeIn   = nodeIn # node 1
        self.nodeOut  = nodeOut # node 2
        self.C  = capacitance # component value
        self.ic = initial_condition

    
    def backward(self, 
                 A : np.array, 
                 b : np.array, 
                 t : float,
                 deltaT : float,
                 current_branch : int, 
                 ):
        #
        # v(t0+dt) = v(t0) + 1/C \int_{t0}^{t0+dt}j(t)dt
        #
        R = deltaT/self.C # dt/C
        G = (1/R) # C/dt
        A[self.nodeIn , self.nodeIn]  +=  G
        A[self.nodeIn , self.nodeOut] += -G
        A[self.nodeOut, self.nodeIn]  += -G
        A[self.nodeOut, self.nodeOut] +=  G
        b[self.nodeIn]                +=  G*self.ic # +C/dt v(t0)
        b[self.nodeOut]               += -G*self.ic # -C/dt v(t0)
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, b, x):
        self.ic = x[self.nodeIn] - x[self.nodeOut]


    @classmethod
    def from_nl( cls, params : Union[Tuple[str, str, int, int, float] , Tuple[str, str, int, int, float, float]] ) -> Capacitor:
        # Capacitor: 'C', name, nodeIn, nodeOut, capacitance, ic=0
        if params[0]!="C":
            raise InvalidElement("Invalid parameters for Capacitor: expected 'C' as first element.")
        return Capacitor(nodeIn=params[2], nodeOut=params[3], capacitance=params[4], name=params[1] , initial_condition=params[5] if len(params) > 5 else 0)



#
# Indutor
#
class Indutor(Element):

    def __init__(self,
                 nodeIn             : int,
                 nodeOut            : int,
                 inductance         : float,
                 initial_condition  : float=0,
                 name               : str=""
                ):
        """
        Initializes a new instance of the class.

        Parameters:
        a (int): The first node (node 1).
        b (int): The second node (node 2).
        inductance (float): The inductance value of the component.
        initial_condition (float, optional): The initial condition of the component. Defaults to 0.
        name (str, optional): The name of the component. Defaults to an empty string.
        """
        Element.__init__(self, name)
        self.nodeIn  = a  # node 1
        self.nodeOut = b  # node 2
        self.L  = inductance  # component value
        self.ic = initial_condition  # initial condition
        


    #
    # j(t0+dt) = j(t0) + 1/L \int_{t0}^{t0+dt}v(t)dt
    #
    def backward(self, 
                 A : np.array, 
                 b : np.array, 
                 t : float,
                 deltaT : float,
                 current_branch : int, 
                 ):

        current_branch+=1
        jx = current_branch
        R = self.L/deltaT # L/dt
        A[self.nodeIn, jx]   +=  1 # current out node a
        A[self.nodeOut, jx]  += -1 # current in node b
        A[jx, self.nodeIn]   += -1 # Va
        A[jx, self.nodeOut]  +=  1 # Vb
        A[jx, jx]            += R
        b[jx]                += R*self.ic
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, b, x):
        self.ic = x[self.jx]


    @classmethod
    def from_nl( cls, params : Union[Tuple[str, str, int, int, float] , Tuple[str, str, int, int, float, float]] ) -> Indutor:
        # Inductor: 'L', name, nodeIn, nodeOut, inductance, ic=0
        if params[0]!="L":
            raise InvalidElement("Invalid parameters for Inductor: expected 'L' as first element.")
        return Indutor(nodeIn=params[2], nodeOut=params[3], inductance=params[4], name=params[1] , initial_condition=params[5] if len(params) > 5 else 0)
