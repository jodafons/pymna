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

__all__ = ["Simulator"]

import numpy as np

from typing import List, Dict
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
from pymna.exceptions import ImpossibleSolution


class Simulator:

    def __init__(self , temperature : float=25, max_nodes : int=10):
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
        while t <= end_time:


            A                = np.zeros( (max_nodes, max_nodes) )
            b                = np.zeros( (max_nodes, ))
            x_newton_raphson = np.zeros( b.shape )
            x                = np.zeros( b.shape )


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
                    x_newton_raphson    = (np.random.rand( x_newton_raphson.shape[0] ) % 100) + 1
                    number_of_guesses   = 0
                    number_of_execution_newton_raphson = 0

                    while not stop_newton_raphson:
                    
                        if number_of_execution_newton_raphson == max_number_of_newton_raphson:
                            if number_of_guesses > max_number_of_guesses:
                                raise ImpossibleSolution("Its not possible to found a solution to this problem.")
                            x_newton_raphson = (np.random.rand(x.shape[0]) % 100) + 1
                            number_of_guesses+=1
                            number_of_execution_newton_raphson=0

                        current_branch   = circuit.number_of_nodes
                        for elm in circuit.elements:
                            current_branch = elm.backward(A,b,x,x_newton_raphson,t,delta_t,current_branch)

                        if reshape:
                            max_nodes = current_branch+1 + 1 # +1 for the ground node
                            A = A[0:max_nodes, 0:max_nodes]
                            b = b[0:max_nodes]
                            x = x[0:max_nodes]
                            x_newton_raphson = x_newton_raphson[0:max_nodes]
                            reshape=False

                        print("A")
                        print(A)
                        print("b")
                        print(b)
                        
                        x = self.solve(A,b)
                        print("x")
                        print(x)
                        print("x_newton_raphson")
                        print(x_newton_raphson)



                        tolerance = np.abs( x - x_newton_raphson ).max()
                        print(tolerance)

                        print("------------")

                        #print(tolerance)
                        if tolerance > max_tolerance:
                            x = x_newton_raphson.copy()
                            number_of_execution_newton_raphson += 1
                        else:
                            stop_newton_raphson = True
                    # end of Newton Raphson

                else:
                    current_branch   = circuit.number_of_nodes
                    for elm in circuit.elements:
                        current_branch = elm.backward(A,b,x,x_newton_raphson,t,delta_t,current_branch)
                    if reshape:
                        max_nodes = current_branch+1 + 1 # +1 for the ground node
                        A = A[0:max_nodes, 0:max_nodes]
                        b = b[0:max_nodes]
                        x = x[0:max_nodes]
                        x_newton_raphson = x_newton_raphson[0:max_nodes]
                        reshape=False
        
                    x = self.solve(A,b)
          
                # update ICs
                for elm in circuit.elements:
                    elm.update( b, x )
                
                print(x)

                internal_step += 1

            # end of internal step

            t += delta_t
            times.append(t)
            internal_step = 0
            e.append( x )

        e = np.array(e)
        result = {"t":times}
        for node_name, node_idx in circuit.nodes.items():
            result[ node_name ] = e[ :, node_idx ] 
        return result


    def solve( self, A, b) -> np.array:
        x = np.linalg.solve(A[1::, 1::],b[1::])
        return np.concatenate(([0],x))




    def run_from_nl( self, nl_path : str ):

        circuit    = Circuit()

        with open(nl_path, 'r') as f:
            lines = f.readlines()

            number_of_nodes = int(lines[0].strip())
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
                elif element == "V":
                    type_source = params[2]
                    if type_source == "SIN":
                        circuit += SinusoidalVoltageSource.from_nl(params)
                    elif type_source == "PULSE":
                        circuit += PulseVoltageSource.from_nl(params)
                elif element == "I":
                    type_source = params[2]
                    if type_source == "SIN":
                        circuit += SinusoidalCurrentSource.from_nl(params)
                    elif type_source == "PULSE":
                        circuit += PulseCurrentSource.from_nl(params)
                else:
                    raise ValueError(f"Unknown element type: {element}")        

            print(simu_config)
            if '.TRAN' in simu_config[0]:
                # .TRAN
                end_time  = float(simu_config[1])
                step_time = float(simu_config[2])
                method    = simu_config[3]
                max_number_of_internal_step = int(simu_config[4])
                use_ic = True if simu_config[5]=='UIC' else False

                result = self.transient(circuit, end_time, step_time,
                                        max_number_of_internal_step=max_number_of_internal_step,
                                        )

            elif '.AC' in simu_config[0]:
                # .AC LIN/OCT/DEC total_of_steps, freq_start, freq_end 
                scale = simu_config[0].split()[1]
                steps = int(simu_config[1])
                freq_start = float(simu_config[2])
                freq_end = float(simu_config[3])
                result = self.ac(circuit, freq_start, freq_end, stepsPerDecade=steps)


            return result

