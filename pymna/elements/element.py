
__all__ = [
            "Step",
            "Element",
        ]

import numpy as np

from typing import Tuple
from abc import ABC, abstractmethod


class Step(ABC):
    def __init__(self, 
                 max_nodes: int,
                 x_newton_raphson: np.array=None,
                 t: float=0,
                 dt: float=0,
                 current_branch: int=0,
                 internal_step: int = 0,
                 omega = 0,

            ):
        self.A = np.zeros( (max_nodes, max_nodes) )
        self.b = np.zeros( (max_nodes, ))
        self.dt = dt
        self.internal_step = internal_step
        self.t = t
        self.current_branch = current_branch
        self.x_newton_raphson = x_newton_raphson
        self.omega = omega
  
             
    def solve( self ) -> np.array:
        max_nodes = self.current_branch+1    
        self.A = self.A[0:max_nodes, 0:max_nodes]
        self.b = self.b[0:max_nodes]
        x = np.linalg.solve(self.A[1::, 1::],self.b[1::])
        return np.concatenate(([0],x))



class Element(ABC):
    def __init__(self, name: str, nolinear_element: bool = False):
        """
        Initializes an instance of the Element class.

        Parameters:
        name (str): The name of the element.
        """
        self.name = name
        self.nolinear_element = nolinear_element
 
    def update( self,  x : np.array):
        pass

    def backward(self, step : Step ):
        pass

    def forward(self, step : Step ):
        pass

    def trap(self, step : Step ):
        pass

    def fourier(self, step : Step ):
        pass
 



def transcondutance( A              : np.array,
                     nodeIn         : int,
                     nodeOut        : int,
                     controlNodeIn  : int,
                     controlNodeOut : int,
                     Gm             : float
                    ):
    A[nodeIn , controlNodeIn  ] +=  Gm
    A[nodeIn , controlNodeOut ] += -Gm
    A[nodeOut, controlNodeIn  ] += -Gm
    A[nodeOut, controlNodeOut ] +=  Gm


def condutance( A : np.array,
                nodeIn : int,
                nodeOut : int,
                G : float):
    transcondutance(A, nodeIn, nodeOut, nodeIn, nodeOut, G)    

