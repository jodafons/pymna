
__all__ = [
            "MOSFET",
        ]

import numpy as np

from pymna.elements import Element, Step
from pymna.elements.extended.diode import Diode
from pymna.exceptions import InvalidElement
from typing import Tuple, Union


class MOSFET(Element):

    def __init__(self, 
                 mosfet_type  : str,
                 collector    : int, 
                 base         : int, 
                 source       : int,
                 W            : float,
                 L            : float,
                 lambda       : float=0.05,
                 K            : float=0.0001,
                 Vth          : float=1,
                 name         : str=""
            ):

        Element.__init__(self,name, nolinear_element=True)
        self.collector = collector
        self.base = base
        self.source = source
        self.W = W
        self.L = L
        self.Lambda = lambda
        self.K = K
        self.Vth = Vth
        if mosfet_type not in ["N", "P"]:
            raise InvalidElement(f"Invalid MOSFET type: {mosfet_type}. Expected 'N' or 'P'.")
        self.mosfet_type = bjt_type

    def backward(self, 
                 step : Step
                 ):

    
        gate = self.gate 

        # ACMQ's book, pag. 93 and 94
        if self.mosfet_type == "N": # is N-channel MOSFET
            if step.x_newton_raphson[self.drain] > step.x_newton_raphson[self.source]:
                drain = self.drain 
                source = self.source
            else:
                drain = self.source
                source = self.drain
            
            vgs = 2 if (t==0 & inter==0) else step.x_newton_raphson[gate] - step.x_newton_raphson[source]
            vds = step.x_newton_raphson[drain] - step.x_newton_raphson[source]

        else: # 'P' is P-channel MOSFET
            if step.x_newton_raphson[self.drain] < step.x_newton_raphson[self.source]:
                drain = self.drain 
                source = self.source
            else:
                drain = self.source
                source = self.drain 
            
            vgs = 2 if (t==0 & inter==0) else -1*(step.x_newton_raphson[gate] - step.x_newton_raphson[source])
            vds = -1*(step.x_newton_raphson[drain] - step.x_newton_raphson[source])


        # Parameters for the MOSFET model
        if vgs > self.Vth:
            vds = step.x_newton_raphson[drain] - step.x_newton_raphson[source]
            # saturation region
            if vds > vgs - self.Vth:
                # Gm = (K * (W/L)) * (2*(vgs - Vth) * (1+Lambda * vds))
                Gm = ( self.K * (self.W/self.L) ) * (2*(vgs - self.Vth) * (1+self.Lambda * vds) )
                # iD = K W/L (vgs - Vth)^2  * (1 + lambda * vds)
                iD = self.K * (self.W/self.L) * (vgs - self.Vth)**2 * (1+self.Lambda*vds)
                # Gds = K W/L (vgs - Vth)^2  * lambda
                Gds = self.K * (self.W/self.K) * (vgs - self.Vth)**2 * self.Lambda
            else: # triode region when vds < vgs - self.Vth:
                # Gm = (K * (W/L)) * (2*(vgs - Vth) - vds) * (1+Lambda * vds)
                iD = self.K * (self.W/self.L) * (2*(vgs-self.Vth)*vds - vds**2) * (1+self.Lambda * vds)
                # Gm = K * (W/L) * (2*vds*(1+Lambda*vds))
                Gm = self.K*(self.W/self.L) * (2*vds*(1+self.Lambda*vds))
                # Gds = K * (W/L) * (2*(vgs - Vth) - vds + 4*Lambda*(vgs - Vth) - 3*Lambda*vds**2)
                Gds = self.K * (self.W/self.L) * (2*(vgs-self.Vth) - 2*vds + 4*self.Lambda*(vgs-self.Vth) - 3*self.Lambda*vds**2) 
        else:
            # cut region
            iD = Gm = Gds = 0

        condutance( A, drain, source, Gds)
        transcondutance( A, drain, source, gate, source, Gm)
        ID = CurrentSource(drain, source, iD)
        ID.backward(step)

    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, int, str]):
        """
        Creates a BJT instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, int, int, int, str]): A tuple containing the parameters for the BJT.

        Returns:
        BJT: An instance of the BJT class.
        """
        if params[0][0] != "Q":
            raise InvalidElement("Invalid parameters for BJT: expected 'Q' as first element.")
        return BJT(bjt_type=params[4], collector=int(params[1]), base=int(params[2]), emitter=int(params[3]), name=params[0])

