

__all__ = ["Circuit"]

from typing           import Union, List
from pymna.units      import MOhm, MHz, Ohm, nF

class Circuit:
    
    def __init__(self, 
                 name : str=""
                 ):

        self.name       = name
        self.elements   = []
        self.gnd        = 0
        self.nodes      = {self.gnd:0}
        self.n_nodes    = 0
        self.has_nonlinear_elements = False

    def node( self, node : Union[int,str] ) -> int:
        if node not in self.nodes.keys():
            self.n_nodes+=1
            self.nodes[node]=self.n_nodes
        return self.nodes[node]

    def __call__(self, node : Union[int,str]) -> int:
        """Allows to use the circuit as a callable to get the node number."""
        return self.node(node)

    def __add__(self, elm ):
        self.elements.append(elm)
        if not self.has_nonlinear_elements:
            self.has_nonlinear_elements = elm.nonlinear_element
        return self

    @property
    def number_of_nodes(self):
        return self.n_nodes

    def to_nl( self ) -> str:
        output = f"{self.number_of_nodes}\n"
        for elm in self.elements:
            output+=elm.to_nl()+"\n"
        return output

          