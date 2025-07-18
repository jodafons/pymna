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

from typing import List
from pymna.elements.circuit import Circuit

class Simulator:

    def __init__(self , temperature : float=25, max_nodes : int=1000):
        self.temperature = temperature
        self.max_nodes = max_nodes

    

    def ac(self, circuit : Circuit ) -> List:
        pass



    def transient(self, 
                      circuit                      : Circuit, 
                      end_time                     : float, 
                      step_time                    : float,
                      tolerance                    : float=1,
                      max_number_of_internal_step  : int=1,
                      max_number_of_guesses        : int=100,
                      max_number_of_newton_raphson : int=20,
                      step_factor                  : float=1e9,
                      
                       ) -> List:
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
                    x_newton_raphson = np.random.rand( x.shape )
                    number_of_guesses = 0
                    number_of_execution_newton_raphson = 0

                    while not stop_newton_raphson:
                    
                        if number_of_execution_newton_raphson == self.max_number_of_newton_raphson:
                            if number_of_guesses > self.max_number_of_guesses:
                                raise ImpossibleSolution("Its not possible to found a solution to this problem.")
                            x_newton_raphson = np.random.rand(x.shape)
                            number_of_guesses+=1
                            number_of_execution_newton_raphson=0

                        current_branch   = circuit.number_of_nodes
                        for elm in circuit.elements:

                            current_branch = elm.backward(A,b,x,x_newton_raphson,t,delta_t,current_branch)

                        if reshape:
                            max_nodes = current_branch+1
                            A = A[0:max_nodes, 0:max_nodes]
                            b = b[0:max_nodes]
                            #x = x[0:current_branch+1]
                            x_newton_raphson = x_newton_raphson[0:max_nodes]
                            reshape=False

                        x = self.solve(A,b)
                        tolerance = np.abs( x - x_newton_raphson ).max()
                        if tolerance > self.tolerance:
                            x = x_newton_raphson
                            number_of_execution_newton_raphson += 1
                        else:
                            stop_newton_raphson = True
                    # end of Newton Raphson

                else:
                    current_branch   = circuit.number_of_nodes
                    for elm in circuit.elements:
                        current_branch = elm.backward(A,b,x,x_newton_raphson,t,delta_t,current_branch)
                    if reshape:
                        max_nodes = current_branch+1
                        A = A[0:max_nodes, 0:max_nodes]
                        b = b[0:max_nodes]
                        x_newton_raphson = x_newton_raphson[0:max_nodes]
                        reshape=False
            
               
                    x = self.solve(A,b)
          
                # update ICs
                for elm in circuit.elements:
                    elm.update( b, x )

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



