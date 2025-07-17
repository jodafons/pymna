

__all__ = [
            "PulseVoltageSource",
            "SinusoidalVoltageSource",
        ]

import numpy as np

from pymna import enumerator as enum
from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC



def sin(t                : float,
        amplitude        : float,
        frequency        : float,
        number_of_cycles : int,
        dc               : float=0,
        angle            : float=0,
        alpha            : float=0,
        delay            : float=0
        ) -> float:
    """
    Calculates the value of a sinusoidal voltage source at time t.
    """
    if (t < delay) or (t>(delay + (1/frequency)*number_of_cycles)):
        V = dc + amplitude * np.sin( (np.pi * angle)/180 )
    else:
        V = (dc + amplitude*np.exp( -1 * alpha * (t-delay) )) * np.sin( 2*np.pi*frequency*(t-delay) + (np.pi*angle)/180 )
    return V


def pulse(t               : float,
          step            : float,
          amplitude_1     : float,
          amplitude_2     : float,
          T               : float,
          rise_time       : float=0,
          fall_time       : float=0,
          time_on         : float=0,
          delay           : float=0
        ) -> float:
    """
    Calculates the value of a pulse voltage source at time t.
    """
    rise_time = step if rise_time==0 else rise_time
    fall_time = step if fall_time==0 else fall_time
    if (t <= (self.T*self.number_of_cycles+self.delay)) and t>self.delay:
        t-=delay
        while (t>T):
            t-=T
        if (t>=0) and (t<rise_time):
            slope = (amplitude_2-amplitude_1)/rise_time
            V = amplitude_1 + t*slope
        elif (t>=rise_time) and (t<=(rise_time+time_on)):
            V = amplitude_2
        elif (t>(rise_time+time_on)) and (t<=(rise_time+time_on+fall_time)):
            slope = (amplitude_1 - amplitude_2)/fall_time
            V = amplitude_2 + (t-(rise_time+time_on))*slope
        else: # t> (rise_time+time_on+fall_time)
            V = amplitude_1
    else:
        V = amplitude_1
    return V


def dc(dc    : float 
       ) -> float:
    """
    Returns a constant DC voltage value.
    """
    return dc



class Source:
    def __init__(self,
                 name     : str,
                 nodeIn  : int,
                 nodeOut : int,
                 ):
        """
        Initializes a Source object.
        This class represents a source in a circuit, which can be used to
        provide voltage or current to a circuit.
        """
        self.nodeIn = nodeIn
        self.nodeOut = nodeOut
        self.name     = name





class SinusoidalVoltageSource(Source):

    def __init__(self,
                 nodeIn  : int,
                 nodeOut  : int,
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
            Initializes an instance of the IndependentSource class.

            This class represents an independent source in a circuit simulation,
            characterized by its amplitude, frequency, number of cycles, and other
            parameters that define its behavior.

            Parameters:
            nodeIn (int): The input node of the source.
            nodeOut (int): The output node of the source.
            amplitude (float): The peak amplitude of the source.
            frequency (float): The frequency of the source in Hertz.
            number_of_cycles (int): The number of cycles the source will operate.
            dc (float, optional): The DC offset of the source. Defaults to 0.
            delay (float, optional): The delay before the source starts. Defaults to 0.
            angle (float, optional): The phase angle of the source in degrees. Defaults to 0.
            alpha (float, optional): The damping factor of the source. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.

            """

            IndependentSource.__init__(self, name, nodeIn, nodeOut)
            self.amplitude = amplitude
            self.frequency = frequency
            self.number_of_cycles = number_of_cycles
            self.dc        = dc
            self.angle     = angle
            self.alpha     = alpha
            self.delay     = delay

    def backward(self, 
                 A : np.array, 
                 b : np.array, 
                 t : float,
                 deltaT : float,
                 current_branch : int, 
                 ):
   
        current_branch += 1
        jx = current_branch
        V = self.sin(t, self.amplitude, 
                        self.frequency, 
                        self.number_of_cycles, 
                        self.dc, 
                        self.angle, 
                        self.alpha, 
                        self.delay)

        # Update the matrix A and vector b for the voltage source
        A[self.nodeIn, jx]  +=  1
        A[self.nodeOut, jx] += -1
        A[jx, self.nodeIn]  += -1
        A[jx, self.nodeOut] +=  1
        b[jx] += V
        return current_branch



    @classmethod
    def from_nl( cls, params : Union[Tuple[str, str, int, int, float] , Tuple[str, str, int, int, float, float]] ) -> Indutor:
        # Inductor: 'L', name, noIn, noOut, inductance, ic=0
        if params[0]!="L":
            raise InvalidElement("Invalid parameters for Inductor: expected 'L' as first element.")
        return Indutor(noIn=params[2], noOut=params[3], inductance=params[4], name=params[1] , initial_condition=params[5] if len(params) > 5 else 0)



    @classmethod
    def from_nl( cls, params : Union[Tuple[str, str, int, int, float, float, int, float, float, float]] ) -> SinusoidalVoltageSource:
        """
        Creates an instance of SinusoidalVoltageSource from a tuple of parameters.
        
        Parameters:
        params (tuple): A tuple containing the parameters for the source.
        
        Returns:
        SinusoidalVoltageSource: An instance of the SinusoidalVoltageSource class.
        """
        if params[0] != 'Vsin':
            raise InvalidElement("Invalid parameters for SinusoidalVoltageSource: expected 'Vsin' as first element.")
        return SinusoidalVoltageSource(nodeIn=params[2], 
                                        nodeOut=params[3], 
                                        amplitude=params[4], 
                                        frequency=params[5], 
                                        number_of_cycles=params[6],
                                        dc=params[7],
                                        delay=params[8],
                                        angle=params[9],
                                        alpha=params[10],
                                        name=params[1])



class PulseVoltageSource(Source):

    def __init__(self,
             nodeIn    : int,
             nodeOut    : int,
             amplitude_1 : float,
             amplitude_2 : float,
             T           : float,
             number_of_cycles : int=1,
             delay       : float=0,
             rise_time   : float=0,
             fall_time   : float=0,
             time_on     : float=0,
             angle       : float=0,
             alpha       : float=0,
             name        : str=""
            ):
        """
        Initializes a Source object for a circuit simulation.

        This class represents a source in a circuit, which can provide 
        varying amplitudes and frequencies over a specified number of cycles. 
        The source can be configured with parameters such as rise time, 
        fall time, and delay to simulate real-world behavior.

        Parameters:
        nodeIn (int): The input node of the source.
        nodeOut (int): The output node of the source.
        amplitude_1 (float): The first amplitude value for the source.
        amplitude_2 (float): The second amplitude value for the source.
        T (float): The period of the source signal.
        number_of_cycles (int, optional): The number of cycles to simulate. Default is 1.
        delay (float, optional): The delay before the source starts. Default is 0.
        rise_time (float, optional): The time it takes for the signal to rise to its peak. Default is 0.
        fall_time (float, optional): The time it takes for the signal to fall to zero. Default is 0.
        time_on (float, optional): The duration for which the source is active. Default is 0.
        angle (float, optional): The phase angle of the source signal. Default is 0.
        alpha (float, optional): The damping factor for the source signal. Default is 0.
        name (str, optional): The name of the source. Default is an empty string.

        """
        
        Source.__init__(self, nodeIn, nodeOut, name=name)
        self.amplitude = amplitude
        self.frequency = frequency
        self.number_of_cycles = number_of_cycles
        self.dc        = dc
        self.angle     = angle
        self.alpha     = alpha
        self.delay     = delay


    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        V = self.pulse(t,...)
        A[self.nodeIn,self.jx] +=  1
        A[self.nodeOut,self.jx] += -1
        A[self.jx, self.nodeIn] += -1
        A[self.jx, self.nodeOut] +=  1
        b[self.jx] += -V
        return current_branch




class VoltageSourceControlByVoltage(Source):

    # This class represents a voltage source controlled by another voltage source.
    # The letter is 'E'.
    def __init__(self, 
                 nodeIn          : int,
                 nodeOut         : int,
                 controlNodeIn  : int,
                 controlNodeOut : int,
                 Av               : float,
                 name             : str=""
            ):
        """
        Initializes a Source object.

        Parameters:
        nodeIn (int): The input node identifier.
        nodeOut (int): The output node identifier.
        Av (float): The voltage gain.
        name (str, optional): The name of the source. Defaults to an empty string.

        This constructor calls the parent class's __init__ method to initialize
        the node identifiers and sets the voltage gain.
        """
        
        Source.__init__(self, nodeIn, nodeOut, name=name)
        self.Av = Av
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut


    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        current_branch += 1
        jx = current_branch
        A[self.nodeIn , jx]         +=  1
        A[self.nodeOut , jx]        += -1
        A[jx, self.nodeIn]          += -1
        A[jx, self.nodeOut]         += 1
        A[jx, self.controlNodeIn]  += self.Av
        A[jx, self.controlNodeOut] += -self.Av 
        return current_branch


    @classmethod
    def from_nl( cls, params : Union[Tuple[str, str, int, int, int, int, float]] ) -> VoltageSourceControlByVoltage:
        # VoltageSourceControlByVoltage: 'E', name, noIn, noOut, control_noIn, control_noOut, Av
        if params[0] != 'E':
            raise InvalidElement("Invalid parameters for VoltageSourceControlByVoltage: expected 'E' as first element.")
        return VoltageSourceControlByVoltage( nodeIn=params[2], 
                                              nodeOut=params[3], 
                                              controlNodeIn=params[4], 
                                              controlNodeOut=params[5], 
                                              Av=params[6],
                                              name=params[1])
 

class CurrentSourceControlByVoltage:
   
   # This class represents a current source controlled by a voltage source.
   # The letter if 'F'
    def __init__(self, 
             nodeIn  : int,
             nodeOut : int,
             controlNodeIn  : int,
             controlNodeOut : int,
             Ai       : float,
             name : str=""
            ):
        """
        Initializes a Source object.

        Parameters:
        nodeIn (int): The input node identifier.
        nodeOut (int): The output node identifier.
        Ai (float): The current gain.
        name (str, optional): The name of the source. Defaults to an empty string.
        
        Calls the parent class's __init__ method to initialize the node identifiers.
        """
        Source.__init__(self, nodeIn, nodeOut, name=name)
        self.Ai = Ai
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut



    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        current_branch += 1
        jx = current_branch
        A[self.controlNodeIn , jx]   +=  1
        A[self.controlNodeOut, jx]   += -1
        A[jx, self.controlNodeIn]    += -1
        A[jx, self.controlNodeOut]   +=  1
        A[self.nodeIn , jx]          +=  self.Ai
        A[self.nodeOut , jx]         += -self.Ai
        return current_branch


class CurrentSourceControlByVoltage(Source):
    
    # This class represents a current source controlled by a voltage source.
    # The letter is 'G'.
    def __init__(self, 
             nodeIn  : int,
             nodeOut : int,
             controlNodeIn  : int,
             controlNodeOut : int,
             Gm       : float,
             name     : str=""
            ):
        """
        Initializes a Source object with the given parameters.

        Parameters:
        nodeIn (int): The input node of the source.
        nodeOut (int): The output node of the source.
        controlNodeIn (int): The control input node for the source.
        controlNodeOut (int): The control output node for the source.
        Gm (float): Transconductance gain of the source.
        name (str, optional): The name of the source. Defaults to an empty string.

        """
        Source.__init__(self, nodeIn, nodeOut, name=name)
        self.Gm = Gm
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        current_branch += 1
        jx = current_branch
        A[self.nodeIn , jx       ] +=  self.Ai
        A[self.nodeOut , jx      ] += -self.Ai
        A[jx, self.nodeIn        ] += -1
        A[jx, self.nodeOut       ] +=  1
        A[jx, self.controlNodeIn ] +=  1
        A[jx, self.controlNodeOut] += -1
        return current_branch


class VoltageSourceControlByCurrent(Source):

    # This class represents a voltage source controlled by a current source.
    # The letter is 'H'.
    def __init__(self, 
                 nodeIn         : int,
                 nodeOut        : int,
                 controlNodeIn  : int,
                 controlNodeOut : int,
                 Rm             : float,
                 name           : str=""
            ):
        """
     
        """
        
        Source.__init__(self, nodeIn, nodeOut, name=name)
        self.Rm = Rm
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut


    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):
        
        current_branch += 1
        # current main branch
        jx = current_branch
        current_branch += 1
        # current control branch
        jy = current_branch

        A[self.nodeIn  , jx       ] +=  1 # I
        A[self.nodeOut , jx       ] += -1 # I
        A[self.controlNodeIn  , jy] +=  1 # I
        A[self.controlNodeOut, jy ] += -1 # I
        A[jx, self.controlNodeIn  ] += -1 # V
        A[jx, self.controlNodeOut ] +=  1 # V
        A[jx, self.controlNodeIn  ] += -1 # V
        A[jx, self.controlNodeOut ] +=  1 # V
        A[jx,jy]                    += self.Rm

        return current_branch

