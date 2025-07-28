
__all__ = [
            "Element",
            "Source",
        ]

import numpy as np

from typing import Tuple
from abc import ABC, abstractmethod

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
        """
        Updates the internal state of the element based on the provided parameters.

        Parameters:
        x : np.array
            The state vector or array that is part of the update operation.
        """
        pass

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
            """
            Computes the backward operation for the given parameters.

            Parameters:
            A : array-like
                The input matrix or array used in the backward computation.
            b : array-like
                The input vector or array that is part of the backward operation.
            t : float, optional
                The current time step (default is 0).
            deltaT : float, optional
                The time increment (default is 0).
            current_branch : int, optional
                The index of the current branch being processed (default is 0).

            Returns:
            int
                Returns 0 as a placeholder for the backward operation result.
            """
            return 0

    def forward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
            """
            Computes the backward operation for the given parameters.

            Parameters:
            A : array-like
                The input matrix or array used in the backward computation.
            b : array-like
                The input vector or array that is part of the backward operation.
            t : float, optional
                The current time step (default is 0).
            deltaT : float, optional
                The time increment (default is 0).
            current_branch : int, optional
                The index of the current branch being processed (default is 0).

            Returns:
            int
                Returns 0 as a placeholder for the backward operation result.
            """
            return 0

    def trap(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
            """
            Computes the backward operation for the given parameters.

            Parameters:
            A : array-like
                The input matrix or array used in the backward computation.
            b : array-like
                The input vector or array that is part of the backward operation.
            t : float, optional
                The current time step (default is 0).
            deltaT : float, optional
                The time increment (default is 0).
            current_branch : int, optional
                The index of the current branch being processed (default is 0).

            Returns:
            int
                Returns 0 as a placeholder for the backward operation result.
            """
            return 0

    def gear(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
            """
            Computes the backward operation for the given parameters.

            Parameters:
            A : array-like
                The input matrix or array used in the backward computation.
            b : array-like
                The input vector or array that is part of the backward operation.
            t : float, optional
                The current time step (default is 0).
            deltaT : float, optional
                The time increment (default is 0).
            current_branch : int, optional
                The index of the current branch being processed (default is 0).

            Returns:
            int
                Returns 0 as a placeholder for the backward operation result.
            """
            return 0

    def fourier(self, 
                A : np.array, 
                b : np.array, 
                w : float) -> int:
        """
        Computes the Fourier transform of a given signal.

        Parameters:
        A (float): Amplitude of the signal.
        b (float): Phase shift of the signal.
        w (float): Frequency of the signal.

        Returns:
        float: The result of the Fourier transform calculation.

        Note:
        This method currently returns 0 as a placeholder.
        """

        return 0
 

class Source:
    
    def __init__(self,
                 name    : str,
                 nodeIn  : int,
                 nodeOut : int,
                 ):
        """
        Initializes a Source object.
        This class represents a source in a circuit, which can be used to
        provide voltage or current to a circuit.

        Parameters:
            name (str): The name of the source.
            nodeIn (int): The input node number.
            nodeOut (int): The output node number.
        """
        self.nodeIn   = nodeIn
        self.nodeOut  = nodeOut
        self.name     = name


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


from . import sources
__all__.extend( sources.__all__ )
from .sources import *

from . import basics
__all__.extend( basics.__all__ )
from .basics import *

from . import logic
__all__.extend( logic.__all__ )
from .logic import *

from . import extended
__all__.extend( extended.__all__ )
from .extended import *
