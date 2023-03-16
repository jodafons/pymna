

__all__ = ["Indutor"]

from pymna.elements.element import Element
from pymna.elements.constants import *
from pymna.exceptions import InvalidElement
from pymna.simulator import config

#
# Indutor
#
class Indutor(Element):

    def __init__(self, netlist):

        self.element = netlist[0]

        # check if this stamp is valid for the current netlist line
        # netlist = ['L', node 1, node 2, value, initial condition = 0]
        if (self.element = Indutor) and len(netlist) != 5:
            raise InvalidElement(f"Element with name {self.element} don't match with the element class.")

        jx = config.currents + 1
        config.currents+=1

        self.a  = netlist[1] # node 1
        self.b  = netlist[2] # node 2
        self.jx = jx
        self.L  = netlist[3] # component value
        self.ic = netlist[4] # initial condition
        


    #
    # j(t0+dt) = j(t0) + 1/L \int_{t0}^{t0+dt}v(t)dt
    #
    def backward_stamp(self, A, b):

        R = self.L/config.deltaT # L/dt
        A[self.a][self.jx]  +=  1 # current out node a
        A[self.b][self.jx]  += -1 # current in node b
        A[self.jx][self.a]  += -1 # Va
        A[self.jx][self.b]  +=  1 # Vb
        A[self.jx][self.jx] += R
        b[self.jx]          += R*self.ic
        

    #
    # Update all initial conditions
    #
    def backward_update(self, x):
        self.ic = x[self.jx]


