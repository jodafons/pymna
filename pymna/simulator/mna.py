"""
This module contains the Simulator class, which is responsible for simulating electrical circuits.
The Simulator can perform both AC analysis and transient analysis of circuits defined by the Circuit class.
It utilizes numerical methods, including the Newton-Raphson method, to solve nonlinear equations that arise during the simulation.

Classes:
- Simulator: A class that simulates the behavior of electrical circuits.

Methods:
- __init__: Initializes the Simulator with temperature and maximum nodes.
- ac: Performs AC analysis on a given circuit (not yet implemented).
- transient: Simulates the transient response of a circuit over a specified time period.
- solve: Solves the linear equation Ax = b using NumPy's linear algebra solver.
"""
"""

"""

__all__ = [
    "Simulator",
    "Method"
]


import enum 
import numpy as np

from typing           import List, Dict, Tuple
from pymna.circuit    import Circuit
from pymna.elements   import Capacitor
from pymna.elements   import Resistor
from pymna.elements   import NoLinearResistor
from pymna.elements   import Inductor
from pymna.elements   import OpAmp
from pymna.elements   import SinusoidalVoltageSource, SinusoidalCurrentSource
from pymna.elements   import PulseVoltageSource, PulseCurrentSource
from pymna.elements   import VoltageSourceControlByCurrent
from pymna.elements   import CurrentSourceControlByVoltage
from pymna.elements   import VoltageSourceControlByVoltage
from pymna.elements   import CurrentSourceControlByCurrent
from pymna.elements   import VoltageSource, CurrentSource
from pymna.elements   import NOT, AND, NAND, OR, NOR, XOR, XNOR
from pymna.exceptions import ImpossibleSolution


class Method(enum.Enum):
    """
    Enumeration of methods for integration.
    """
    TRAPEZOIDAL = "trapezoidal"
    FORWARD_EULER = "forward_euler"
    BACKWARD_EULER = "backward_euler"
    


class Simulator:

    def __init__(self , temperature : float=25, max_nodes : int=1000):
        self.temperature = temperature
        self.max_nodes = max_nodes

    def ac(self, circuit : Circuit ,
               freqInitial : float,
               freqEnd     : float,
               stepsPerDecade : int=10,
               ) -> (Dict, Dict):
            """
            Perform AC analysis on the given circuit over a specified frequency range.

            This function computes the frequency response of the circuit by solving
            the circuit equations at logarithmically spaced frequencies between 
            freqInitial and freqEnd. It returns the magnitude and phase of the 
            circuit's response for each node.

            Parameters:
            circuit (Circuit): The circuit object containing the elements and nodes.
            freqInitial (float): The starting frequency for the analysis (in Hz).
            freqEnd (float): The ending frequency for the analysis (in Hz).
            stepsPerDecade (int): The number of frequency steps per decade (default is 10).

            Returns:
            Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
                A tuple containing two dictionaries:
                - mod_result: Magnitude response for each node at the specified frequencies.
                - phase_result: Phase response for each node at the specified frequencies.
            """
            freqs = np.logspace(np.log10(freqInitial), np.log10(freqEnd), num=stepsPerDecade )
            omegas = 2 * np.pi * freqs
            reshape = True
            max_nodes = self.max_nodes
            e = []
            
            for w in omegas:

                A                = np.zeros( (max_nodes, max_nodes) , dtype=np.complex128)
                b                = np.zeros( (max_nodes, ), dtype=np.complex128)

                current_branch  = circuit.number_of_nodes
                for elm in circuit.elements:
                    current_branch = elm.fourier(A, b, w, current_branch)

                if reshape:
                    max_nodes = current_branch + 1
                    A = A[0:max_nodes, 0:max_nodes]
                    b = b[0:max_nodes]
                    reshape = False

                x = self.solve(A, b)
                e.append(x)

            e = np.array(e)

            mods = 20*np.log10(np.abs(e))
            phases = np.degrees(np.angle(e))
        

            mod_result   = {"freqs":freqs}
            phase_result = {"freqs":freqs}
            for node_name, node_idx in circuit.nodes.items():
                mod_result[ node_name ]   = np.real(mod[ :, node_idx ]) 
                phase_result[ node_name ] = np.real(phases[ :, node_idx ])
            
            return mod_result, phase_result

    def transient(self, 
                  circuit                      : Circuit, 
                  end_time                     : float, 
                  step_time                    : float,
                  max_tolerance                : float=1,
                  max_number_of_internal_step  : int=1,
                  max_number_of_guesses        : int=100,
                  max_number_of_newton_raphson : int=20,
                  step_factor                  : float=1e9,
                  method                       : Method=Method.BACKWARD_EULER
                ) -> Dict:
        """
        Simulates the transient response of a circuit over a specified time period.
        Parameters:
        - circuit (Circuit): The circuit to be simulated.
        - end_time (float): The time at which the simulation ends.
        - step_time (float): The time increment for each simulation step.
        - tolerance (float, optional): The tolerance for convergence in Newton-Raphson method. Default is 1.
        - max_number_of_internal_step (int, optional): Maximum number of internal steps per time increment. Default is 1.
        - max_number_of_guesses (int, optional): Maximum number of guesses for Newton-Raphson method. Default is 100.
        - max_number_of_newton_raphson (int, optional): Maximum iterations for Newton-Raphson method. Default is 20.
        - step_factor (float, optional): Factor to adjust the step size. Default is 1e9.
        
        Returns:
        - List: A list containing the time points and corresponding node voltages.
        
        Notes:
        - The method uses the Newton-Raphson method for solving nonlinear equations.
        - If the solution does not converge within the specified number of iterations or guesses, an exception is raised.
        - The circuit's elements are updated at each internal step based on the computed voltages.
        """

        t                = 0
        e                = []
        times            = []

        reshape=True
        max_nodes = self.max_nodes

        print(f"Transient simulation started with end_time={end_time}, step_time={step_time}")
        print(f"max_number_of_internal_step={max_number_of_internal_step}, max_tolerance={max_tolerance}")
        print(f"Max number of nodes: {circuit.number_of_nodes}")
        col_names = [f"{node_name+1}" for node_name in range(circuit.number_of_nodes)]
        
        while t <= end_time:

            if t==0:
                max_internal_step = 1
                # NOTE: at the beginner, using short step to accomodate the circuit at first loop
                delta_t = (step_time/max_number_of_internal_step)/step_factor
            else:
                max_internal_step = max_number_of_internal_step
                delta_t = step_time/max_number_of_internal_step

            internal_step = 0

            while internal_step < max_internal_step:

                # NOTE: Newton Raphson loop
                # Execute 20 ciclos and if not converge, abort the approximation and repeat the guess
                # If the max number of guess reached (100 guesses), abort the simulation
                if circuit.has_nolinear_elements:

                    stop_newton_raphson = False
                    number_of_guesses   = 0
                    x_newton_raphson    = np.random.rand( max_nodes )%100 + 1
                    number_of_execution_newton_raphson = 0

                    while not stop_newton_raphson:
                    
                        if number_of_execution_newton_raphson == max_number_of_newton_raphson:
                            if number_of_guesses > max_number_of_guesses:
                                raise ImpossibleSolution("Its not possible to found a solution to this problem.")
                            x_newton_raphson    = np.random.rand(max_nodes)%100 + 1
                            number_of_guesses+=1
                            number_of_execution_newton_raphson=0

                        x, max_nodes, col_names = self.solve_system_of_equations(circuit, t, delta_t, max_nodes, method, x_newton_raphson, col_names)
                        x_newton_raphson = x_newton_raphson[0:max_nodes]
                        tolerance = np.abs( x - x_newton_raphson ).max()
                        if tolerance > max_tolerance:
                            x_newton_raphson = x
                            number_of_execution_newton_raphson += 1
                        else:
                            stop_newton_raphson = True
                    # end of Newton Raphson

                # NOTE: if the circuit has no nonlinear elements, we can use the linear solver directly
                else: # circuit has no nonlinear elements
                    x, max_nodes, col_names = self.solve_system_of_equations(circuit, t, delta_t, max_nodes, method, [], col_names)
          
                # update ICs
                for elm in circuit.elements:
                    elm.update( x )
                
                internal_step += 1

            # end of internal step

            t += delta_t
            times.append(t)
            internal_step = 0
            e.append( x )

        e = np.array(e)
        result = {"t":times}
        for col_idx, col_name in enumerate(col_names):            
            result[ col_name ] = e[ :, col_idx+1 ]

        return result

    def solve( self, A, b) -> np.array:
        x = np.linalg.solve(A[1::, 1::],b[1::])
        return np.concatenate(([0],x))

    def solve_system_of_equations( self, 
                                       circuit : Circuit, 
                                       t       : float, 
                                       delta_t : float,
                                       max_nodes : int,
                                       method    : Method,
                                       x_newton_raphson : np.array,
                                       col_names : List[str],
                                    ) -> Tuple[np.array, int]:
            """
            Solves a system of equations for the given circuit using the specified numerical method.

            This method constructs the system of equations based on the circuit elements and 
            applies the chosen numerical method (Backward Euler, Trapezoidal, or Forward Euler) 
            to compute the solution.

            Parameters:
            ----------
            circuit : Circuit
                The circuit object containing elements and node information.
            t : float
                The current time at which the system is being solved.
            delta_t : float
                The time step for the numerical method.
            max_nodes : int
                The maximum number of nodes in the circuit.
            method : Method
                The numerical method to be used for solving the equations.
            x_newton_raphson : np.array
                The initial guess for the Newton-Raphson method.
            col_names : List[str]
                A list to store the names of the columns in the resulting matrix.

            Returns:
            -------
            Tuple[np.array, int]
                A tuple containing:
                - The solution vector `x` as a NumPy array.
                - The updated number of nodes after processing the circuit elements.
                - The updated list of column names.

            Raises:
            ------
            ValueError
                If the specified method is not recognized.
            """
            A                = np.zeros( (max_nodes, max_nodes) )
            b                = np.zeros( (max_nodes, ))
            x                = np.zeros( (max_nodes, ) )
            current_branch   = circuit.number_of_nodes
            for elm in circuit.elements:
                last_branch = current_branch

                if method == Method.BACKWARD_EULER:
                    # NOTE: the backward method of each element returns the current branch
                    current_branch = elm.backward(A,b,x,x_newton_raphson,t,delta_t,current_branch)
                elif method == Method.TRAPEZOIDAl:
                    # NOTE: the trapezoidal method of each element returns the current branch
                    current_branch = elm.trapezoidal(A,b,x,x_newton_raphson,t,delta_t,current_branch)
                elif method == Method.FORWARD_EULER:
                    # NOTE: the forward method of each element returns the current branch
                    current_branch = elm.forward(A,b,x,x_newton_raphson,t,delta_t,current_branch)
                else:
                    # NOTE: if the method is not recognized, raise an error
                    raise ValueError(f"Unknown method: {method}")            
                
                if current_branch > last_branch:
                    col_name = f"J{current_branch}{elm.name}"
                    if not col_name in col_names:
                        col_names.append(col_name)

            max_nodes = current_branch+1
            A = A[0:max_nodes, 0:max_nodes]
            b = b[0:max_nodes]
            x = self.solve(A,b)
            return x, max_nodes, col_names

    def run_from_nl( self, nl_path : str ):
        
        # Resistor:  R<nome> <no+> <no-> <resistencia>
        # VCCS:      G<nome> <io+> <io-> <vi+> <vi-> <transcondutancia>
        # VCVC:      E<nome> <vo+> <vo-> <vi+> <vi-> <ganho de tensao>
        # CCCS:      F<nome> <io+> <io-> <ii+> <ii-> <ganho de corrente>
        # CCVS:      H<nome> <vo+> <vo-> <ii+> <ii-> <transresistencia>
        # Fonte I:   I<nome> <io+> <io-> <tipo de fonte>
        # Fonte V:   V<nome> <vo+> <vo-> <tipo de fonte>
        # Amp. op.:  O<nome> <vo1> <vo2> <vi1> <vi2>
        # Capacitor: C<nome> <no+> <no-> <capacitancia> [IC=<tensao inicial>]
        # Indutor:   L<nome> <no+> <no-> <indutancia> [IC=<corrente inicial>]
        # Indutor 1: X<nome> <no+> <no-> <indutancia> [IC=<corrente inicial>]
        # Ind. mutua:K<nome> <L1> <L2> <coeficiente de acoplamento>
        # Diodo:     D<nome> <no+> <no->
        # Trans. MOS:M<nome> <nod> <nog> <nos> <nob> <tipo> L=<comprimento> W=<largura>
        # Trans. BJT:Q<nome> <noc> <nob> <noe> <tipo>
                
        circuit    = Circuit()

        with open(nl_path, 'r') as f:
            lines = f.readlines()

            number_of_nodes = int(lines[0].strip())

            [circuit.node(n+1) for n in range(number_of_nodes)]
            simu_config = lines.pop().strip().split()

            # Process the line to create circuit elements
            # This part is dependent on the NL file format
            # You would typically parse the line and create Circuit elements here
            for line in lines[1::]:
                line = line.strip()
                # this is to skip comments and empty lines
                if line.startswith('*'):
                    continue

                print(line)
             
                params = line.split()
                element = params[0][0]
                if element == "R":
                    circuit += Resistor.from_nl(params)
                elif element == "C":
                    circuit += Capacitor.from_nl(params)
                elif element == "L":
                    circuit += Inductor.from_nl(params)
                elif element == "N":
                    circuit += NoLinearResistor.from_nl(params)
                elif element == "O":
                    circuit += OpAmp.from_nl(params)
                elif element == "E":
                    circuit += VoltageSourceControlByVoltage.from_nl(params)
                elif element == "F":
                    circuit += CurrentSourceControlByVoltage.from_nl(params)
                elif element == "G":
                    circuit += VoltageSourceControlByCurrent.from_nl(params)
                elif element == "H":
                    circuit += CurrentSourceControlByCurrent.from_nl(params)
                elif element == '>':
                    circuit += NOT.from_nl(params)
                elif element == ')':
                    circuit += AND.from_nl(params)
                elif element == '(':
                    circuit += NAND.from_nl(params)
                elif element == '}':
                    circuit += OR.from_nl(params)
                elif element == '{':
                    circuit += NOR.from_nl(params)
                elif element == ']':
                    circuit += XOR.from_nl(params)
                elif element == '[':
                    circuit += XNOR.from_nl(params)
                elif element == "V":
                    type_source = params[2]
                    if type_source == "SIN":
                        circuit += SinusoidalVoltageSource.from_nl(params)
                    elif type_source == "PULSE":
                        circuit += PulseVoltageSource.from_nl(params)
                    elif type_source == "DC":
                        circuit += VoltageSource.from_nl(params)
                elif element == "I":
                    type_source = params[2]
                    if type_source == "SIN":
                        circuit += SinusoidalCurrentSource.from_nl(params)
                    elif type_source == "PULSE":
                        circuit += PulseCurrentSource.from_nl(params)
                    elif type_source == "DC":
                        circuit += CurrentSource.from_nl(params)
                else:
                    raise ValueError(f"Unknown element type: {element}")

            print(simu_config)
            if '.TRAN' in simu_config[0]:
                # .TRAN
                end_time  = float(simu_config[1])
                step_time = float(simu_config[2])
                method    = simu_config[3]
                if method=="BE":
                    method = Method.BACKWARD_EULER
                elif method=="TR":
                    method = Method.TRAPEZOIDAl
                elif method=="FE":
                    method = Method.FORWARD_EULER
                else:
                    raise ValueError(f"Unknown method: {method}")
                max_number_of_internal_step = int(simu_config[4])
                use_ic = True if simu_config[5]=='UIC' else False
                result = self.transient(circuit, end_time, step_time,
                                        max_number_of_internal_step=max_number_of_internal_step,
                                        method = method
                                        )

            elif '.AC' in simu_config[0]:
                # .AC LIN/OCT/DEC total_of_steps, freq_start, freq_end 
                scale = simu_config[0].split()[1]
                steps = int(simu_config[1])
                freq_start = float(simu_config[2])
                freq_end = float(simu_config[3])
                result = self.ac(circuit, freq_start, freq_end, stepsPerDecade=steps)


            return result

