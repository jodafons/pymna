

__all__ = ["Resistor"]

from pymna.elements.element import Element
from pymna.elements.constants import *
from pymna.exceptions import InvalidElement


#
# Resistor
#
class Resistor(Element):

    def __init__(self, netlist):

        self.element = netlist[0]

        # check if this stamp is valid for the current netlist line
        # netlist = ['R', node 1, node 2, value]
        if (self.element = RESISTOR) and len(netlist) != 4:
            raise InvalidElement(f"Element with name {self.element} don't match with the element class.")

        self.a = netlist[1] # node 1
        self.b = netlist[2] # node 2
        self.R = netlist[3] # component value


    #
    # Backward method
    #
    def backward_stamp(self, A, b):

        G = (1/self.R)
        A[self.a][self.a] +=  G
        A[self.a][self.b] += -G
        A[self.b][self.a] += -G
        A[self.b][self.b] +=  G
    
    #
    # Update all initial conditions
    #
    def backward_update(self,x):
        pass