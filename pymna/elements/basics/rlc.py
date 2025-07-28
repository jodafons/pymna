__all__ = [
            "Resistor",
            "Capacitor",
            "Inductor",
            "NoLinearResistor",
        ]

import numpy as np
from pymna.elements import Element
from pymna.elements.element import condutance
from pymna.elements.sources import CurrentSource
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
        condutance(A, self.nodeIn, self.nodeOut, G)
        return current_branch

    def fourier(self,
                A : np.array,
                b : np.array,
                w : float,
                current_branch : int,
                ):

        G = (1/self.R)
        condutance(A, self.nodeIn, self.nodeOut, G)
        return current_branch    

    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, float]):
        """
        Creates a Resistor instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, int, int, float]): A tuple containing the parameters for the resistor.

        Returns:
        Resistor: An instance of the Resistor class.
        """
        if params[0][0] != "R":
            raise InvalidElement("Invalid parameters for Resistor: expected 'R' as first element.")
        return Resistor(nodeIn=int(params[1]), nodeOut=int(params[2]), resistence=float(params[3]), name=params[0])

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
        """
        Updates the circuit matrices for the capacitor element in backward time step.
        """
        R = dt/self.C # dt/C
        condutance(A, self.nodeIn, self.nodeOut, 1/R)
        Ic = CurrentSource( self.nodeOut, self.nodeIn, self.ic/R)  
        current_branch = Ic.backward(A, b, x, x_newton_raphson, t, dt, current_branch)
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, x):
        self.ic = x[self.nodeIn] - x[self.nodeOut]


    def fourier(self,
                A : np.array,
                b : np.array,
                w : float,
                current_branch : int,
                ):

        Z = 1 / 1j * w * self.C 
        G = 1 / Z  # G = 1 / (j * w * C)
        condutance(A, self.nodeIn, self.nodeOut, G)
        return current_branch


    @classmethod
    def from_nl(cls, params: Union[Tuple[str, int, int, float], Tuple[str, str, int, int, float, float]]):
        """
        Creates a Capacitor instance from a tuple of parameters.

        Parameters:
        params (Union[Tuple[str, int, int, float], Tuple[str, str, int, int, float, float]]): A tuple containing the parameters for the capacitor.

        Returns:
        Capacitor: An instance of the Capacitor class.
        """
        if params[0][0] != "C":
            raise InvalidElement("Invalid parameters for Capacitor: expected 'C' as first element.")
        return Capacitor(nodeIn=int(params[1]), nodeOut=int(params[2]), capacitance=float(params[3]), 
                         name=params[0], initial_condition=float(params[4][3::]) if len(params) > 4 else 0)

#
# Inductor
#
class Inductor(Element):
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
        self.jx = -1  # current branch index, initialized to -1

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
        self.jx = jx
        return current_branch

    #
    # Update all initial conditions
    #
    def update(self, x):
        self.ic = x[self.jx]

    def fourier(self,
                A : np.array,
                b : np.array,
                w : float,
                current_branch : int,
                ):
        current_branch += 1
        jx = current_branch
        Z = 1j * w * self.L  # Z = j * w * L
        A[self.nodeIn, jx]   +=  1  # current out node a
        A[self.nodeOut, jx]  += -1  # current in node b
        A[jx, self.nodeIn]   += -1  # Va
        A[jx, self.nodeOut]  +=  1  # Vb
        A[jx, jx]            += Z  # Impedance


    @classmethod
    def from_nl(cls, params: Union[Tuple[str, int, int, float], Tuple[str, str, int, int, float, float]]):
        """
        Creates an Inductor instance from a tuple of parameters.

        Parameters:
        params (Union[Tuple[str, int, int, float], Tuple[str, str, int, int, float, float]]): A tuple containing the parameters for the inductor.

        Returns:
        Indutor: An instance of the Indutor class.
        """
        if params[0][0] != "L":
            raise InvalidElement("Invalid parameters for Inductor: expected 'L' as first element.")
        return Inductor(nodeIn=int(params[1]), nodeOut=int(params[2]), inductance=float(params[3]), 
                        name=params[0], initial_condition=float(params[4][3::]) if len(params) > 4 else 0)


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
            Element.__init__(self,name, nolinear_element = True)
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
   
        ddp = x_newton_raphson[self.nodeIn] - x_newton_raphson[self.nodeOut]
        if ddp > self.nolinear_voltage_3:
            # Tangente da reta ou derivada da funcao
            G = (self.nolinear_current_4 - self.nolinear_current_3)/(self.nolinear_voltage_4 - self.nolinear_voltage_3)
            I = self.nolinear_current_4 - G*self.nolinear_voltage_4
        elif (ddp <= self.nolinear_voltage_3) and (ddp > self.nolinear_voltage_2):
            # Tangente da reta ou derivada da funcao
            G = (self.nolinear_current_3 - self.nolinear_current_2)/(self.nolinear_voltage_3 - self.nolinear_voltage_2)
            I = self.nolinear_current_3 - G*self.nolinear_voltage_3
        elif (ddp <= self.nolinear_voltage_2) :
            # Tangente da reta ou derivada da funcao
            G = (self.nolinear_current_2 - self.nolinear_current_1)/(self.nolinear_voltage_2 - self.nolinear_voltage_1)
            I = self.nolinear_current_2 - G*self.nolinear_voltage_2
       
        condutance(A, self.nodeIn, self.nodeOut, G)  # Condutance matrix
        I = CurrentSource(self.nodeIn, self.nodeOut, I)  # Current source
        current_branch = I.backward(A, b, x, x_newton_raphson, t, dt, current_branch)  # Update current branch
        return current_branch

    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, float, float, float, float, float, float, float, float]):
        """
        Creates a NoLinearResistor instance from a tuple of parameters.

        Parameters:
        params (Tuple[str, int, int, float, float, float, float, float, float, float, float]): A tuple containing the parameters for the nonlinear resistor.

        Returns:
        NoLinearResistor: An instance of the NoLinearResistor class.
        """
        # Nname, nodeIn, nodeOut, nolinear_voltage_1, nolinear_current_1, 
        # nolinear_voltage_2, nolinear_current_2, nolinear_voltage_3, nolinear_current_3, nonlinear_voltage_4, nolinear_current_4 
        if params[0][0] != "N":
            raise InvalidElement("Invalid parameters for Nonlinear Resistor: expected 'NLR' as first element.")
        return NoLinearResistor(nodeIn=int(params[1]), nodeOut=int(params[2]), 
                                nolinear_voltage_1=float(params[3]), nolinear_current_1=float(params[4]),
                                nolinear_voltage_2=float(params[5]), nolinear_current_2=float(params[6]),
                                nolinear_voltage_3=float(params[7]), nolinear_current_3=float(params[8]),
                                nolinear_voltage_4=float(params[9]), nolinear_current_4=float(params[10]), name=params[0])
