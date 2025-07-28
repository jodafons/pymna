__all__ = [
            "BJT",
        ]

import numpy as np

from pymna.elements import Element, Step
from pymna.exceptions import InvalidElement
from typing import Tuple, Union


class BJT(Element):

    def __init__(self, 
                 bjt_type  : str,
                 collector : int, 
                 base      : int, 
                 emitter   : int, 
                 alpha     : float=0.99,
                 alpha_R   : float=0.5,
                 name      : str=""
            ):
        """
        Initializes a BJT (Bipolar Junction Transistor) element with specified parameters.

        Parameters:
        collector (int): The collector node of the BJT.
        base (int): The base node of the BJT.
        emitter (int): The emitter node of the BJT.
        id (float, optional): The current through the BJT (default is 1.0).
        name (str, optional): The name of the BJT element (default is an empty string).
        """
        Element.__init__(self,name ,nolinear_element=True)
        self.collector = collector
        self.base = base
        self.emitter = emitter
        self.alpha = alpha
        self.alpha_R = alpha_R
        self.bjt_type = bjt_type

    def backward(self, 
                 step : Step
                 ):

        # Pag. 90 from ACQM's book
        if self.bjt_type=="N": # is NPN
            Dbe = Diode(self.base, self.emitter)
            ICB = CurrentSource(self.collector, self.base, self.alpha*Dbe.Id )
            # transcondutance
            icb= CurrentSourceControlByVoltage(self.collector, self.base, self.base, self.emitter, self.alpha*Dbe.g)
            Dbc = Diode(self.base, self.collector)
            IBE = CurrentSource(self.emitter, self.base, self.alpha_R*Dbc.Id)
            # transcondutance
            ibe= CurrentSourceControlByVoltage(self.emitter, self.base, self.base, self.collector, self.alpha_R*Dbc.g)
            model = [Dbe, ICB, icb, Dbc, IBE, ibe]

        else: # 'P' is PNP
            Deb = Diode(self.emitter, self.base)
            ICB = CurrentSource(self.base, self.collector, self.alpha*Deb.Id )
            # transcondutance
            icb= CurrentSourceControlByVoltage(self.collector, self.base, self.base, self.emitter, self.alpha*Deb.g)
            Dcb = Diode(self.collector, self.base)
            IBE = CurrentSource(self.base, self.emitter, self.alpha_R*Dcb.Id)
            # transcondutance
            ibe= CurrentSourceControlByVoltage(self.emitter, self.base, self.base, self.collector, self.alpha_R*Dcb.g)
            model = [Deb, ICB, icb, Dcb, IBE, ibe]

        for elm in model:
            elm.backward(step)

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
