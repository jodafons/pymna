

__all__ = ["Capacitor"]

from pymna.elements.element import Element
from pymna.elements.constants import *
from pymna.exceptions import InvalidElement
from pymna.simulator import config

#
# Capacitor
#
class Capacitor(Element):

    def __init__(self, netlist):

        self.element = netlist[0]

        # check if this stamp is valid for the current netlist line
        # netlist = ['C', node 1, node 2, value, initial condition = 0]
        if (self.element = CAPACITOR) and len(netlist) != 5:
            raise InvalidElement(f"Element with name {self.element} don't match with the element class.")

        self.a  = netlist[1] # node 1
        self.b  = netlist[2] # node 2
        self.C  = netlist[3] # component value
        self.ic = netlist[4] # initial condition


    #
    # v(t0+dt) = v(t0) + 1/C \int_{t0}^{t0+dt}j(t)dt
    #
    def backward_stamp(self, A, b):

        R = config.deltaT/self.C # dt/C
        G = (1/R) # C/dt
        A[self.a][self.a] +=  G
        A[self.a][self.b] += -G
        A[self.b][self.a] += -G
        A[self.b][self.b] +=  G
        b[self.a]         +=  G*self.ic
        b[self.b]         += -G*self.ic

    #
    # Update all initial conditions
    #
    def backward_update(self, x):
        self.ic = x[self.a] - x[self.b]


