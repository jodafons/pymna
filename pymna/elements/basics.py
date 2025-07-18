
"""
This module defines basic electrical elements used in circuit simulations, including:
- Resistor
- Capacitor
- Inductor

Each class represents a specific element and provides methods for updating circuit matrices and handling initial conditions.
"""



__all__ = [
            "Resistor",
            "Capacitor",
            "Indutor",
            "Ampop",
            "NoLinearResistor"
        ]

import numpy as np

from pymna import enumerator as en1um
from pymna.elements import Element
from pymna.exceptions import InvalidElement
from typing import Tuple, Union

#
# Resistor
#
class Resistor(Element):
    """
    Represents a resistor element in a circuit.

    Attributes:
    nodeIn (int): The first node connected by the resistor.
    nodeOut (int): The second node connected by the resistor.
    R (float): The resistance value of the resistor.
    """
    # This class represents a resistor element in a circuit.
    #               
    #             /\    /\    /\
    # nodeIn o---/  \  /  \  /  \  /---o nodeOut
    #                \/    \/    \/
    #
    def __init__(self, 
                 nodeIn       : int, 
                 nodeOut      : int, 
                 resistence : float, 
                 name       : str=""
            ):
        """
        Initializes an instance of the Resistor class.

        Parameters:
        nodeIn (int): The first node connected by the element.
        nodeOut (int): The second node connected by the element.
        resistence (float): The resistance value of the element.
        name (str, optional): The name of the element. Defaults to an empty string.
        """
        Element.__init__(self,name)
        self.nodeIn = nodeIn # node 1
        self.nodeOut = nodeOut # node 2
        self.R = resistence # component value

    #
    # Backward method
    #
    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:

        G = (1/self.R)
        A[self.nodeIn , self.nodeIn ] +=  G
        A[self.nodeIn , self.nodeOut] += -G
        A[self.nodeOut, self.nodeIn ] += -G
        A[self.nodeOut, self.nodeOut] +=  G
        return current_branch

    @classmethod
    def from_nl(cls, params: Tuple[str, str, int, int, float]) -> Resistor:
        """
        Creates a Resistor instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, str, int, int, float]): A tuple containing the parameters for the resistor.

        Returns:
        Resistor: An instance of the Resistor class.
        """
        if params[0] != "R":
            raise InvalidElement("Invalid parameters for Resistor: expected 'R' as first element.")
        return Resistor(nodeIn=params[2], nodeOut=params[3], resistence=params[4], name=params[1])

#
# Capacitor
#
class Capacitor(Element):
    """
    Represents a capacitor element in a circuit.

    Attributes:
    nodeIn (int): The first node connected to the capacitor.
    nodeOut (int): The second node connected to the capacitor.
    C (float): The capacitance value of the capacitor.
    ic (float): The initial condition of the capacitor.
    """

    # This class represents a capacitor element in a circuit.
    #
    #               | |
    #               | |
    #  nodeIn o-----| |-----o nodeOut
    #               | |
    #               | |
    #
    def __init__(self,
                 nodeIn             : int,
                 nodeOut            : int,
                 capacitance        : float,
                 initial_condition  : float=0,
                 name               : str=""
                ):
        """
        Initializes a new instance of the Capacitor class.

        Parameters:
        nodeIn (int): The first node connected to the element (node 1).
        nodeOut (int): The second node connected to the element (node 2).
        capacitance (float): The capacitance value of the element.
        initial_condition (float, optional): The initial condition of the element. Defaults to 0.
        name (str, optional): The name of the element. Defaults to an empty string.
        """
        Element.__init__(self,name)
        self.nodeIn   = nodeIn # node 1
        self.nodeOut  = nodeOut # node 2
        self.C  = capacitance # component value
        self.ic = initial_condition

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
    
        R = dt/self.C # dt/C
        G = (1/R) # C/dt
        A[self.nodeIn , self.nodeIn]  +=  G
        A[self.nodeIn , self.nodeOut] += -G
        A[self.nodeOut, self.nodeIn]  += -G
        A[self.nodeOut, self.nodeOut] +=  G
        b[self.nodeIn]                +=  G*self.ic # +C/dt v(t0)
        b[self.nodeOut]               += -G*self.ic # -C/dt v(t0)
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, b, x):
        self.ic = x[self.nodeIn] - x[self.nodeOut]

    @classmethod
    def from_nl(cls, params: Union[Tuple[str, str, int, int, float], Tuple[str, str, int, int, float, float]]) -> Capacitor:
        """
        Creates a Capacitor instance from a tuple of parameters.

        Parameters:
        params (Union[Tuple[str, str, int, int, float], Tuple[str, str, int, int, float, float]]): A tuple containing the parameters for the capacitor.

        Returns:
        Capacitor: An instance of the Capacitor class.
        """
        if params[0] != "C":
            raise InvalidElement("Invalid parameters for Capacitor: expected 'C' as first element.")
        return Capacitor(nodeIn=params[2], nodeOut=params[3], capacitance=params[4], name=params[1], initial_condition=params[5] if len(params) > 5 else 0)

#
# Indutor
#
class Indutor(Element):
    """
    Represents an inductor element in a circuit.

    Attributes:
    nodeIn (int): The first node connected by the inductor.
    nodeOut (int): The second node connected by the inductor.
    L (float): The inductance value of the inductor.
    ic (float): The initial condition of the inductor.
    """

    def __init__(self,
                 nodeIn             : int,
                 nodeOut            : int,
                 inductance         : float,
                 initial_condition  : float=0,
                 name               : str=""
                ):
        """
        Initializes a new instance of the Indutor class.

        Parameters:
        nodeIn (int): The first node (node 1).
        nodeOut (int): The second node (node 2).
        inductance (float): The inductance value of the component.
        initial_condition (float, optional): The initial condition of the component. Defaults to 0.
        name (str, optional): The name of the component. Defaults to an empty string.
        """
        Element.__init__(self, name)
        self.nodeIn  = nodeIn  # node 1
        self.nodeOut = nodeOut  # node 2
        self.L  = inductance  # component value
        self.ic = initial_condition  # initial condition

    #
    # j(t0+dt) = j(t0) + 1/L \int_{t0}^{t0+dt}v(t)dt
    #
    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:

        current_branch += 1
        jx = current_branch
        R = self.L / dt  # L/dt
        A[self.nodeIn, jx]   +=  1  # current out node a
        A[self.nodeOut, jx]  += -1  # current in node b
        A[jx, self.nodeIn]   += -1  # Va
        A[jx, self.nodeOut]  +=  1  # Vb
        A[jx, jx]            += R
        b[jx]                += R * self.ic
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, b, x):
        self.ic = x[self.jx]

    @classmethod
    def from_nl(cls, params: Union[Tuple[str, str, int, int, float], Tuple[str, str, int, int, float, float]]) -> Indutor:
        """
        Creates an Indutor instance from a tuple of parameters.

        Parameters:
        params (Union[Tuple[str, str, int, int, float], Tuple[str, str, int, int, float, float]]): A tuple containing the parameters for the inductor.

        Returns:
        Indutor: An instance of the Indutor class.
        """
        if params[0] != "L":
            raise InvalidElement("Invalid parameters for Inductor: expected 'L' as first element.")
        return Indutor(nodeIn=params[2], nodeOut=params[3], inductance=params[4], name=params[1], initial_condition=params[5] if len(params) > 5 else 0)

#
# Ampop
#
class Ampop(Element):

    # This class represents an operational amplifier element in a circuit.
    # The letter is 'O'.
    def __init__(self, 
                 controlNodePos : int,
                 controlNodeNeg : int,
                 nodeOut        : int,
                 name           : str=""
    ):
        """
        Initializes an instance of the Ampop class.

        Parameters:
        controlNodePos (int): The positive control node of the operational amplifier.
        controlNodeNeg (int): The negative control node of the operational amplifier.
        nodeOut (int): The positive output node of the operational amplifier.
        name (str, optional): The name of the operational amplifier. Defaults to an empty string.
        """
        Element.__init__(self, name)
        self.controlNodePos = controlNodePos
        self.controlNodeNeg = controlNodeNeg
        self.nodeOutPos     = nodeOut
        self.nodeOutNeg     = 0


    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
 
        current_branch += 1
        jx = current_branch
        A[self.nodeOutPos, jx]     +=  1 
        A[self.nodeOutNeg, jx]     += -1
        A[jx, self.controlNodePos] += -1
        A[jx, self.controlNodeNeg] +=  1
        return current_branch

    @classmethod
    def from_nl(cls, params: Tuple[str, str, int, int, int]) -> Ampop:
        """
        Creates an Ampop instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, str, int, int, int]): A tuple containing the parameters for the operational amplifier.

        Returns:
        Ampop: An instance of the Ampop class.
        """
        if params[0] != "O":
            raise InvalidElement("Invalid parameters for Operational Amplifier: expected 'O' as first element.")
        return Ampop(controlNodePos=params[2], controlNodeNeg=params[3], nodeOut=params[4], name=params[1])


class NoLinearResistor(Element):

    # This class represents a nonlinear resistor element in a circuit.
    # The letter is 'N'.
    #
    # This class represents a resistor element in a circuit.
    #              
    #            +-------------------+--+ 
    #            | /\    /\    /\    |==|
    # nodeIn o---+/  \  /  \  /  \  /+==+---o nodeOut
    #            |    \/    \/    \/ |==|
    #            +-------------------+--+ 
    #
    def __init__(self, 
                     nodeIn             : int, 
                     nodeOut            : int, 
                     nolinear_voltage_1 : float,
                     nolinear_current_1 : float,
                     nolinear_voltage_2 : float,
                     nolinear_current_2 : float,
                     nolinear_voltage_3 : float,
                     nolinear_current_3 : float,
                     nolinear_voltage_4 : float,
                     nolinear_current_4 : float,
                     name               : str=""
                ):
            """
            Initializes a nonlinear element with specified nodes and voltage/current characteristics.

            Parameters:
            nodeIn (int): The input node of the element (node 1).
            nodeOut (int): The output node of the element (node 2).
            nolinear_voltage_1 (float): The first nonlinear voltage value.
            nolinear_current_1 (float): The first nonlinear current value.
            nolinear_voltage_2 (float): The second nonlinear voltage value.
            nolinear_current_2 (float): The second nonlinear current value.
            nolinear_voltage_3 (float): The third nonlinear voltage value.
            nolinear_current_3 (float): The third nonlinear current value.
            nolinear_voltage_4 (float): The fourth nonlinear voltage value.
            nolinear_current_4 (float): The fourth nonlinear current value.
            name (str, optional): The name of the element. Defaults to an empty string.
            """
            Element.__init__(self,name)
            self.nodeIn             = nodeIn  # node 1
            self.nodeOut            = nodeOut # node 2
            self.nolinear_voltage_1 = nolinear_voltage_1
            self.nolinear_current_1 = nolinear_current_1
            self.nolinear_voltage_2 = nolinear_voltage_2
            self.nolinear_current_2 = nolinear_current_2
            self.nolinear_voltage_3 = nolinear_voltage_3
            self.nolinear_current_3 = nolinear_current_3
            self.nolinear_voltage_4 = nolinear_voltage_4
            self.nolinear_current_4 = nolinear_current_4


    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
   
        ddp = x_newton_raphson[self.noteIn] - x_newton_raphson[self.nodeOut]
        if ddp > self.nolinear_voltage_3:
            # Tangente da reta ou derivada da funcao
            G = (self.nolinear_current_4 - self.nolinear_current_3)/(self.nolinear_voltage_4 - self.nolinear_voltage_3)
            I = self.nolinear_current_4 - G*self.nolinear_voltage_4
        elif (ddp <= self.nolinear_voltage_3) and (ddp > self.nolinear_voltage_2):
            # Tangente da reta ou derivada da funcao
            G = (self.nolinear_current_3 - self.nolinear_current_2)/(self.nolinear_voltage_3 - self.nolinear_voltage_2)
            I = self.nolinear_current_3 - G*self.nolinear_voltage_3
        else: 
            # Tangente da reta ou derivada da funcao
            G = (self.nolinear_current_2 - self.nolinear_current_1)/(self.nolinear_voltage_2 - self.nolinear_voltage_1)
            I = self.nolinear_current_2 - G*self.nolinear_voltage_2

        A[self.nodeIn, self.nodeIn]   +=  G		# G
        A[self.nodeIn, self.nodeOut]  += -G		# G
        A[self.nodeOut, self.nodeIn]  += -G		# G
        A[self.nodeOut, self.nodeOut] +=  G		# G
        b[self.nodeIn]  += -I		# Fonte de corrente referente ao modelo do resistor nao linear indo do no 1 para o no 2.
        b[self.nodeOut] +=  I		# Fonte de corrente referente ao modelo do resistor nao linear indo do no 1 para o no 2.
        return current_branch


    @classmethod
    def from_nl(cls, params: Tuple[str, str, int, int, float, float, float, float, float, float, float, float]) -> NoLinearResistor:
        """
        Creates a NoLinearResistor instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, str, int, int, float, float, float, float, float, float, float, float]): A tuple containing the parameters for the nonlinear resistor.

        Returns:
        NoLinearResistor: An instance of the NoLinearResistor class.
        """
        # N, name, nodeIn, nodeOut, nolinear_voltage_1, nolinear_current_1, 
        # nolinear_voltage_2, nolinear_current_2, nolinear_voltage_3, nolinear_current_3, nonlinear_voltage_4, nolinear_current_4 
        if params[0] != "N":
            raise InvalidElement("Invalid parameters for Nonlinear Resistor: expected 'NLR' as first element.")
        return NoLinearResistor(nodeIn=params[2], nodeOut=params[3], 
                                nolinear_voltage_1=params[4], nolinear_current_1=params[5],
                                nolinear_voltage_2=params[6], nolinear_current_2=params[7],
                                nolinear_voltage_3=params[8], nolinear_current_3=params[9],
                                nolinear_voltage_4=params[10], nolinear_current_4=params[11], name=params[1])
