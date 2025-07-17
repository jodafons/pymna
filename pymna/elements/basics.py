

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

from pymna import enumerator as enum
from pymna.elements import Element
from typing import Tuple



#
# Resistor
#
class Resistor(Element):

    #               
    #        /\    /\    /\
    # a o---/  \  /  \  /  \  /---o b
    #           \/    \/    \/
    #
    def __init__(self, 
             a : int, 
             b : int, 
             resistence : float, 
             name : str=""
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
        self.a = a # node 1
        self.b = b # node 2
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
        A[self.a, self.a] +=  G
        A[self.a, self.b] += -G
        A[self.b, self.a] += -G
        A[self.b, self.b] +=  G
        return current_branch



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
             a : int,
             b : int,
             capacitance : float,
             initial_condition : float=0,
             name : str=""
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
        self.a  = a # node 1
        self.b  = b # node 2
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
        A[self.a, self.a] +=  G
        A[self.a, self.b] += -G
        A[self.b, self.a] += -G
        A[self.b, self.b] +=  G
        b[self.a]         +=  G*self.ic # +C/dt v(t0)
        b[self.b]         += -G*self.ic # -C/dt v(t0)
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, b, x):
        self.ic = x[self.a] - x[self.b]



#
# Indutor
#
class Indutor(Element):

    def __init__(self,

             a : int,
             b : int,
             inductance : float,
             initial_condition : float=0,
             name : str=""
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
        self.a  = a  # node 1
        self.b  = b  # node 2
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
        A[self.a, jx]  +=  1 # current out node a
        A[self.b, jx]  += -1 # current in node b
        A[jx, self.a]  += -1 # Va
        A[jx, self.b]  +=  1 # Vb
        A[jx, jx]      += R
        b[jx]          += R*self.ic
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, b, x):
        self.ic = x[self.jx]



