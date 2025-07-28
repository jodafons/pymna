__all__ = [
            "Diode",
        ]

import numpy as np

from pymna.elements import Element, Step
from pymna.exceptions import InvalidElement
from typing import Tuple, Union


class Diode(Element):
  
    def __init__(self, 
                     nodeIn : int, 
                     nodeOut: int, 
                     IS     : float=3.7751345e-14,
                     VT     : float=25e-3,
                     name   : str=""
                ):
            """
            Initializes a semiconductor element with specified parameters.

            Parameters:
            nodeIn (int): The input node of the semiconductor.
            nodeOut (int): The output node of the semiconductor.
            IS (float, optional): The saturation current (default is 3.7751345e-14).
            VT (float, optional): The thermal voltage (default is 25e-3).
            name (str, optional): The name of the semiconductor element (default is an empty string).

            This constructor calls the parent class's constructor to initialize the element with the given name.
            It also sets the input and output nodes, saturation current, and thermal voltage for the semiconductor.
            """
            Element.__init__(self,name)
            self.nodeIn = nodeIn
            self.nodeOut = nodeOut
            self.IS=IS
            self.VT=VT
            self.Id=0
            self.g=0

    def backward(self, 
                 step : Step
                 ):

        if t==0:
            ddp=0.6
        else:
            ddp = step.x_newton_raphson[self.nodeIn] - step.x_newton_raphson[self.nodeOut]
            ddp = 0.9 if ddp > 0.9 else ddp

        self.g  = (IS/VT)*np.exp( ddp )
        self.Id = IS * (np.exp(ddp/VT) - 1) - self.g * ddp
        # condutance
        condutance( A, self.nodeIn, self.nodeOut, self.g)
        I = CurrentSource(self.nodeIn, self.nodeOut, self.Id)
        I.backward(step)
        
    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, ]):
        """
        Creates a Diode instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, int, int]): A tuple containing the parameters for the diode.

        Returns:
        Diode: An instance of the Diode class.
        """
        if params[0][0] != "D":
            raise InvalidElement("Invalid parameters for Diode: expected 'D' as first element.")
        return Diode(nodeIn=int(params[1]), nodeOut=int(params[2]), name=params[0])