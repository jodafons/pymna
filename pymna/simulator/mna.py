__all__ = ["Simulator"]

import numpy as np

from typing import List
from pymna.elements.circuit import Circuit

class Simulator:

    def __init__(self , temperature : float=25, max_nodes : int=100):
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

        A                = np.zeros( (self.max_nodes, self.max_nodes) )
        b                = np.zeros( (self.max_nodes, 1))
        x                = np.zeros( b.shape )
        x_newton_raphson = np.zeros( b.shape )
        tolerance        = 1
        t                = 0
        result           = []
        current_branch   = circuit.number_of_nodes+1
       
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


                        for elm in circuit.elements:
                            current_branch = elm.backward(A,b,t,delta_t,current_branch)
                        x = self.solve(A,b)

                        tolerance = np.abs( x - x_newton_raphson ).max()
                        if tolerance > self.tolerance:
                            x = x_newton_raphson
                            number_of_execution_newton_raphson += 1
                        else:
                            stop_newton_raphson = True
                    # end of Newton Raphson

                else:
                    for elm in circuit.elements:
                        current_branch = elm.backward(A,b,t,delta_t,current_branch)
                    x = self.solve(A,b)

                
                # update ICs
                for elm in circuit.elements:
                    elm.update( b, x )

                internal_step += 1

            # end of internal step

            t += delta_t
            internal_step = 0
            result.append( x )

        return result


    def solve( self, A, b) -> np.array:
        return np.linalg.solve(A[1:, 1:], b[1:])
