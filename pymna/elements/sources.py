

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
                 node_in  : int,
                 node_out : int,
                 ):
        """
        Initializes a Source object.
        This class represents a source in a circuit, which can be used to
        provide voltage or current to a circuit.
        """
        self.node_in = node_in
        self.node_out = node_out
        self.name     = name





class SinusoidalVoltageSource(Source):

    def __init__(self,
                 node_in  : int,
                 node_out  : int,
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
            node_in (int): The input node of the source.
            node_out (int): The output node of the source.
            amplitude (float): The peak amplitude of the source.
            frequency (float): The frequency of the source in Hertz.
            number_of_cycles (int): The number of cycles the source will operate.
            dc (float, optional): The DC offset of the source. Defaults to 0.
            delay (float, optional): The delay before the source starts. Defaults to 0.
            angle (float, optional): The phase angle of the source in degrees. Defaults to 0.
            alpha (float, optional): The damping factor of the source. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.

            """

            IndependentSource.__init__(self, name, node_in, node_out)
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
        V = self.sin(t, self.amplitude, self.frequency, self.number_of_cycles, self.dc, self.angle, self.alpha, self.delay)
        A[self.node_in, jx] +=  1
        A[self.node_out, jx] += -1
        A[jx, self.node_in] += -1
        A[jx, self.node_out] +=  1
        b[jx] += V
        return current_branch

    def update(self, b, x ):
        pass



class PulseVoltageSource(Source):

    def __init__(self,
             node_in    : int,
             node_out    : int,
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
        node_in (int): The input node of the source.
        node_out (int): The output node of the source.
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
        
        Source.__init__(self, node_in, node_out, name=name)
        self.amplitude = amplitude
        self.frequency = frequency
        self.number_of_cycles = number_of_cycles
        self.dc        = dc
        self.angle     = angle
        self.alpha     = alpha
        self.delay     = delay


    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        V = self.pulse(t,...)
        A[self.node_in,self.jx] +=  1
        A[self.node_out,self.jx] += -1
        A[self.jx, self.node_in] += -1
        A[self.jx, self.node_out] +=  1
        b[self.jx] += -V
        return current_branch




class VoltageSourceControlByVoltage(Source):

    def __init__(self, 
             node_in  : int,
             node_out : int,
             Av       : float,
             name : str=""
            ):
        """
        Initializes a Source object.

        Parameters:
        node_in (int): The input node identifier.
        node_out (int): The output node identifier.
        Av (float): The voltage gain.
        name (str, optional): The name of the source. Defaults to an empty string.

        This constructor calls the parent class's __init__ method to initialize
        the node identifiers and sets the voltage gain.
        """
        
        Source.__init__(self, node_in, node_out, name=name)
        self.Av = Av

    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        current_branch += 1
        jx = current_branch
        A[self.node_in , jx]         +=  1
        A[self.node_out , jx]        += -1
        A[jx, self.node_in]          += -1
        A[jx, self.node_out]         += 1
        A[jx, self.control_node_in]  += self.Av
        A[jx, self.control_node_out] += -self.Av 
        return current_branch


 

class CurrentSourceControlByVoltage:

