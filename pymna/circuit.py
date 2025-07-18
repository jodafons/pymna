

__all__ = ["Circuit"]

from typing import Union, List
from pymna.elements import Capacitor, Resistor, NoLinearResistor, Ampop
from pymna.elements import SinusoidalVoltageSource



class Circuit:
    """
    Represents an electrical circuit that can contain various elements such as resistors, capacitors, and voltage sources.

    This class allows the user to create a circuit by adding components and defining their connections. 
    It manages nodes and elements within the circuit and provides methods to create common circuit elements.

    Attributes:
    name (str): The name of the circuit.
    elements (list): A list of elements in the circuit.
    gnd (int): The ground node, default is 0.
    nodes (dict): A dictionary mapping node identifiers to their corresponding indices.
    n_nodes (int): The total number of nodes in the circuit.
    has_nolinear_elements (bool): A flag indicating if the circuit contains nonlinear elements.

    Example:
    To create a Chua circuit, you can use the following code:

    ```python
    # Create a circuit
    circuit = Circuit(name="Chua Circuit")

    # Add components to the circuit
    circuit.R('node1', 'node2', 1e3, name='R1')  # Resistor R1
    circuit.R('node2', 'node3', 1e3, name='R2')  # Resistor R2
    circuit.C('node3', 'gnd', 1e-6, name='C1')   # Capacitor C1
    circuit.NoLinearResistor('node1', 'node2', 
                             nolinear_voltage_1=0.5, 
                             nolinear_current_1=0.1, 
                             nolinear_voltage_2=-0.5, 
                             nolinear_current_2=-0.1, 
                             nolinear_voltage_3=0.0, 
                             nolinear_current_3=0.0, 
                             nolinear_voltage_4=0.0, 
                             nolinear_current_4=0.0, 
                             name='Chua Diode')

    circuit.SinusoidalVoltageSource('node1', 'gnd', amplitude=5, frequency=1000, number_of_cycles=10, name='V1')
    ```

    This example sets up a basic Chua circuit with resistors, a capacitor, and a nonlinear resistor (Chua diode) along with a sinusoidal voltage source.
    """
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
          nodeIn            : Union[int,str],
          nodeOut           : Union[int,str],
          capacitance       : float,
          name              : str="",
          initial_condition : float=0
          ) -> Capacitor:
        """
        Creates a capacitor between two nodes in the circuit.

        Parameters:
        nodeIn (Union[int, str]): The input node for the capacitor.
        nodeOut (Union[int, str]): The output node for the capacitor.
        capacitance (float): The capacitance value of the capacitor in Farads.
        name (str, optional): An optional name for the capacitor. Defaults to an empty string.
        initial_condition (float, optional): The initial voltage across the capacitor. Defaults to 0.

        Returns:
        Capacitor: An instance of the Capacitor class.

        Example:
        To use the SinusoidalVoltageSource in an RC circuit:

        ```python
        # Create a circuit
        circuit = Circuit()

        # Add a resistor and capacitor
        circuit.R('in', 'out', 1*kOhm, name='R1')  # 1k ohm resistor
        circuit.SinusoidalVoltageSource("in", circuit.gnd, amplitude=5*V, frequency=60*Hz, number_of_cycles=10)
        circuit.C( 'out', circuit.gnd, 50*uF, name='C1' )  # 50uF capacitor
        ```

        This example creates an RC circuit with a sinusoidal voltage source connected to a resistor and capacitor.

        """
        C = Capacitor( self.node(nodeIn), 
                                     self.node(nodeOut), 
                                     capacitance, 
                                     initial_condition=initial_condition, 
                                     name=name)
        self+=C
        return C
    
    def R(self,
          nodeIn     : Union[int,str],
          nodeOut    : Union[int,str],
          resistence : float,
          name       : str="",
          ) -> Resistor:
        """
        Creates a resistor between two nodes in the circuit.

        Parameters:
        
        nodeIn (Union[int, str]): The input node where the resistor is connected.
        nodeOut (Union[int, str]): The output node where the resistor is connected.
        resistence (float): The resistance value of the resistor in ohms.
        name (str, optional): An optional name for the resistor. Defaults to an empty string.
        
        Returns:
        Resistor: An instance of the Resistor class representing the created resistor.
        
        Example:
        To use the SinusoidalVoltageSource in an RC circuit:
        
        ```python
        # Create a circuit
        circuit = Circuit()
        # Add a resistor and capacitor
        circuit.R('in', 'out', 1*kOhm, name='R1')  # 1k ohm resistor
        circuit.SinusoidalVoltageSource("in", circuit.gnd, amplitude=5*V, frequency=60*Hz, number_of_cycles=10)
        circuit.C( 'out', circuit.gnd, 50*uF, name='C1' )  # 50uF capacitor
        ```
        
        This example creates an RC circuit with a sinusoidal voltage source connected to a resistor and capacitor.
        """
        R = Resistor( self.node(nodeIn), self.node(nodeOut), 
                      resistence, 
                      name=name)
        self+=R
        return R

    def NoLinearResistor(self,
                         nodeIn             : Union[int,str],
                         nodeOut            : Union[int,str],
                         nolinear_voltage_1 : float,
                         nolinear_current_1 : float,
                         nolinear_voltage_2 : float,
                         nolinear_current_2 : float,
                         nolinear_voltage_3 : float,
                         nolinear_current_3 : float,
                         nolinear_voltage_4 : float,
                         nolinear_current_4 : float,
                         name               : str=""
    ) -> NoLinearResistor:
        """
        Creates a nonlinear resistor between two nodes in the circuit.

        Parameters:
        nodeIn (Union[int, str]): The input node where the nonlinear resistor is connected.
        nodeOut (Union[int, str]): The output node where the nonlinear resistor is connected.
        nolinear_voltage_1 (float): The first voltage point for the nonlinear characteristic.
        nolinear_current_1 (float): The current at the first voltage point.
        nolinear_voltage_2 (float): The second voltage point for the nonlinear characteristic.
        nolinear_current_2 (float): The current at the second voltage point.
        nolinear_voltage_3 (float): The third voltage point for the nonlinear characteristic.
        nolinear_current_3 (float): The current at the third voltage point.
        nolinear_voltage_4 (float): The fourth voltage point for the nonlinear characteristic.
        nolinear_current_4 (float): The current at the fourth voltage point.
        name (str, optional): An optional name for the nonlinear resistor. Defaults to an empty string.

        Returns:
        NoLinearResistor: An instance of the NoLinearResistor class.

        """
        R = NoLinearResistor( self.node(nodeIn),
                              self.node(nodeOut),
                              nolinear_voltage_1,
                              nolinear_current_1,
                              nolinear_voltage_2,
                              nolinear_current_2,
                              nolinear_voltage_3,
                              nolinear_current_3,
                              nolinear_voltage_4,
                              nolinear_current_4,
                              name=name)
        self.+=R
        return R


    def Ampop(self,
               nodePositive : Union[int,str],
               nodeNegative : Union[int,str],
               nodeOut      : Union[int,str],
               name         : str="",
    ) -> Ampop:
        """
        Creates an operational amplifier (op-amp) in the circuit.

        Parameters:
        nodePositive (Union[int, str]): The positive input node of the op-amp.
        nodeNegative (Union[int, str]): The negative input node of the op-amp.
        nodeOut (Union[int, str]): The output node of the op-amp.
        name (str, optional): An optional name for the op-amp. Defaults to an empty string.

        Returns:
        Ampop: An instance of the Ampop class representing the operational amplifier.

       
        """
        A = Ampop(self.node(nodePositive), 
                  self.node(nodeNegative), 
                  self.node(nodeOut), 
                  name=name)
        self+=A
        return A




    #
    # sources
    #

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
        """
        Creates a sinusoidal voltage source in the circuit.

        Parameters:
        positive (Union[int, str]): The positive terminal node of the voltage source.
        negative (Union[int, str]): The negative terminal node of the voltage source.
        amplitude (float): The peak amplitude of the sinusoidal voltage.
        frequency (float): The frequency of the sinusoidal voltage in Hertz.
        number_of_cycles (int): The number of cycles to simulate.
        dc (float, optional): A DC offset added to the sinusoidal voltage. Default is 0.
        delay (float, optional): The delay before the sinusoidal voltage starts. Default is 0.
        angle (float, optional): The phase angle of the sinusoidal voltage in degrees. Default is 0.
        alpha (float, optional): The damping factor for the sinusoidal voltage. Default is 0.
        name (str, optional): An optional name for the voltage source. Default is an empty string.

        Example:
        To use the SinusoidalVoltageSource in an RC circuit:
        
        ```python
        # Create a circuit
        circuit = Circuit()

        # Add a resistor and capacitor
        circuit.R('in', 'out', 1*kOhm, name='R1')  # 1k ohm resistor
        circuit.SinusoidalVoltageSource("in", circuit.gnd, amplitude=5*V, frequency=60*Hz, number_of_cycles=10)
        circuit.C( 'out', circuit.gnd, 50*uF, name='C1' )  # 50uF capacitor
        ```

        This example creates an RC circuit with a sinusoidal voltage source connected to a resistor and capacitor.
        """
        
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
    
