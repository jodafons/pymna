
__all__ = [
    "PulseVoltageSource",
    "PulseCurrentSource",
]

import numpy as np
from pymna.elements import Element, Step
from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC


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

    Parameters:
        t (float): The time at which to calculate the voltage.
        step (float): The time step for the pulse calculation.
        amplitude_1 (float): The first amplitude value for the pulse.
        amplitude_2 (float): The second amplitude value for the pulse.
        T (float): The period of the pulse signal.
        rise_time (float, optional): The time it takes for the signal to rise. Defaults to 0.
        fall_time (float, optional): The time it takes for the signal to fall. Defaults to 0.
        time_on (float, optional): The duration for which the pulse is active. Defaults to 0.
        delay (float, optional): The delay before the pulse starts. Defaults to 0.

    Returns:
        float: The calculated voltage at time t.
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

class PulseVoltageSource(Element):

    def __init__(self,
             nodeIn      : int,
             nodeOut     : int,
             amplitude_1 : float,
             amplitude_2 : float,
             T           : float,
             number_of_cycles : int=1,
             delay       : float=0,
             rise_time   : float=0,
             fall_time   : float=0,
             time_on     : float=0,
             angle       : float=0,
             attenuation : float=0,
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
            angle (float, optional): The phase angle of the source. Default is 0.
            attenuation (float, optional): The damping factor for the source. Default is 0.
            name (str, optional): The name of the source. Default is an empty string.
        """
        Element.__init__(self, name)
        self.nodeIn  = nodeIn
        self.nodeOut = nodeOut
        self.amplitude   = amplitude
        self.frequency   = frequency
        self.number_of_cycles = number_of_cycles
        self.dc          = dc
        self.angle       = angle
        self.attenuation = attenuation
        self.delay       = delay

    def backward(self, 
                 step : Step,
                 ):

        V = self.pulse(step.t,
                        self.amplitude_1,
                        self.amplitude_2,
                        self.T,
                        self.rise_time,
                        self.fall_time,
                        self.time_on,
                        self.delay)

        Vs = VoltageSource(self.nodeIn, self.nodeOut, V)
        Vs.backward(step)

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, str, float, float, float, float, float, float, float, int] ):
        # PulseVoltageSource: 'I/V'name, nodeIn, nodeOut, 'PULSE', AMPLITUDE_1, AMPLITUDE_2, DELAY, RISE_TIME, FALL_TIME, TIME_ON, PERIOUD, NUMBER_OF_CYCLES
        if params[0][0] != 'I' or params[0][0] != 'V':
            raise InvalidElement(f"Invalid parameters for PulseVoltageSource: expected 'I/V' ({params[0]}) as first element.")
        if params[3] != "PULSE" and len(params) != 12:
            raise InvalidElement(f"Invalid parameters for PulseVoltageSource: expected 'PULSE' ({params[3]}) as third element and 12 ({len(params)}) parameters in total.")
        return PulseVoltageSource( nodeIn=int(params[1]),
                                   nodeOut=int(params[2]),
                                   amplitude_1=float(params[4]),
                                   amplitude_2=float(params[5]),
                                   delay=float(params[6]),
                                   rise_time=float(params[7]),
                                   fall_time=float(params[8]),
                                   time_on=float(params[9]),
                                   T=float(params[10]),
                                   number_of_cycles=int(params[11]),
                                   name=params[0])

class PulseCurrentSource(PulseVoltageSource):
    def __init__(self,
             nodeIn      : int,
             nodeOut     : int,
             amplitude_1 : float,
             amplitude_2 : float,
             T           : float,
             number_of_cycles : int=1,
             delay       : float=0,
             rise_time   : float=0,
             fall_time   : float=0,
             time_on     : float=0,
             angle       : float=0,
             attenuation : float=0,
             name        : str=""
            ):
        """
        Initializes a PulseCurrentSource object with the given parameters.
        This class represents a pulse current source in a circuit simulation.
        """
        PulseVoltageSource.__init__(self, 
                                    nodeIn, 
                                    nodeOut, 
                                    amplitude_1, 
                                    amplitude_2, 
                                    T, 
                                    number_of_cycles, 
                                    delay, 
                                    rise_time, 
                                    fall_time, 
                                    time_on, 
                                    angle, 
                                    attenuation, 
                                    name)

    def backward(self, 
                 step : Step,
                 ) -> int:
                 
        I = self.pulse(step.t,
                        self.amplitude_1,
                        self.amplitude_2,
                        self.T,
                        self.rise_time,
                        self.fall_time,
                        self.time_on,
                        self.delay)
        Is = CurrentSource(self.nodeIn, self.nodeOut, I)
        Is.backward(step)
