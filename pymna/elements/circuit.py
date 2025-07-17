

__all__ = ["Circuit"]

from typing import Union, List
from pymna.elements import Capacitor, Resistor
from pymna.elements import SinusoidalVoltageSource

# ... rest of the code ...
__all__ = ["Circuit"]

from typing import Union, List
from pymna.elements import Capacitor, Resistor
from pymna.elements import SinusoidalVoltageSource


class Circuit:

    def __init__(self, 
                 name : str=""
                 ):
        self.name       = name
        self.elements   = []
        self.gnd        = 0
        self.nodes      = {self.gnd:0}
        self.n_nodes    = 0
        self.has_nolinear_elements = False

    def node( self, node : Union[int,str] ) -> int:
        if node not in self.nodes.keys():
            self.n_nodes+=1
            self.nodes[node]=self.n_nodes
        return self.nodes[node]

    def __add__(self, elm ):
        self.elements.append(elm)
        return self

    @property
    def number_of_nodes(self):
        return self.n_nodes


    def C(self,
          a : Union[int,str],
          b : Union[int,str],
          capacitance : float,
          name : str="",
          initial_condition : float=0
          ) -> Capacitor:
        C = Capacitor( self.node(a), 
                       self.node(b), 
                       capacitance, 
                       initial_condition=initial_condition, 
                       name=name)
        self+=C
        return C
    
    def R(self,
          a : Union[int,str],
          b : Union[int,str],
          resistence : float,
          name : str="",
          ) -> Resistor:
        R = Resistor( self.node(a), 
                      self.node(b), 
                      resistence, 
                      name=name)
        self+=R
        return R


    def SinusoidalVoltageSource(self,
                 positive  : Union[int,str],
                 negative  : Union[int,str],
                 amplitude : float,
                 frequency : float,
                 number_of_cycles : int,
                 dc        : float=0,
                 delay     : float=0,
                 angle     : float=0,
                 alpha     : float=0,
                 name      : str=""
                ):

        Vsin = SinusoidalVoltageSource(self.node(positive), 
                                       self.node(negative), 
                                       amplitude, 
                                       frequency, 
                                       number_of_cycles,
                                       dc = dc,
                                       delay = delay,
                                       angle = angle,
                                       alpha = alpha,
                                       name = name)
        self+=Vsin


if __name__ == "__main__":
    from pymna.units import *
    circuit = Circuit(name="RC")
    circuit.SinusoidalVoltageSource("in", circuit.gnd,  amplitude=1*V, freq=60*Hz, name="input")
    circuit.R( "in", "out", 1*kOhm, name="R1")
    circuit.C( "out", circuit.gnd, 50*uF, name="C1" )
    
