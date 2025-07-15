

__all__ = [
            "Resistor",
            "Capacitor",
            "Indutor",
            "parser_resistor_from_netlist_row",
            "parser_capacitor_from_netlist_row",
            "parser_indutor_from_netlist_row",
        ]

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
        Element.__init__(self,name)
        self.a = a # node 1
        self.b = b # node 2
        self.R = resistence # component value


    #
    # Backward method
    #
    def backward(self, A, b, deltaT : float, current_branch : int):
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
        Element.__init__(self,name)
        self.a  = a # node 1
        self.b  = b # node 2
        self.C  = capacitance # component value
        self.ic = initial_condition


    def backward(self, A, b, t : float, deltaT : float, current_branch : int):
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
    def update(self, x):
        self.ic = x[self.a] - x[self.b]



#
# Indutor
#
class Indutor(Element):

    def __init__(self,

                 a : int,
                 b : int,
                 indutance : float,
                 initial_condition : float=0,
                 name : str=""
                ):
        Element.__init__(self,name)
        self.a  = a # node 1
        self.b  = b # node 2
        self.L  = L # component value
        self.ic = ic # initial condition
        


    #
    # j(t0+dt) = j(t0) + 1/L \int_{t0}^{t0+dt}v(t)dt
    #
    def backward(self, A, b, deltaT : float, current_branch : int):
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
    def update(self, x):
        self.ic = x[self.jx]


#
# netlist parsers
#

def parser_resistor_from_netlist_row( row : Tuple ) -> Resistor:
    if row[1]!=enum.Element.RESISTOR and len(row)!=5:
        raise InvalidElement(f"Element with name {row[0]} don't match with the element Resistor.")
    name, element, a, b, resistence = row 
    return Resistor(a,b,resistence,name=name)


def parser_capacitor_from_netlist_row( row : Tuple ) -> Capacitor:
    if row[1]!=enum.Element.CAPACITOR and len(row)!=6:
        raise InvalidElement(f"Element with name {row[0]} don't match with the element Capacitor.")
    name, element, a, b, capacitance, ic = row 
    return Capacitor(a,b,capacitance,initial_condition=ic, name=name)


def parser_indutor_from_netlist_row( row : Tuple ) -> Indutor:
    if row[1]!=enum.Element.CAPACITOR and len(row)!=6:
        raise InvalidElement(f"Element with name {row[0]} don't match with the element Indutor.")
    name, element, a, b, indutance, ic = row 
    return Indutor(a,b,indutance,initial_condition=ic, name=name)




