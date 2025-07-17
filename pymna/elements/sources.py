

"""
This module provides classes and functions for simulating various types of voltage sources 
in electrical circuits. It includes implementations for sinusoidal and pulse voltage sources, 
as well as a constant DC voltage source. The sources can be characterized by parameters such 
as amplitude, frequency, delay, and damping factors, allowing for flexible circuit simulations.

Classes:
- Source: Base class for all sources in the circuit.
- SinusoidalVoltageSource: Represents a sinusoidal voltage source.
- PulseVoltageSource: Represents a pulse voltage source.

Functions:
- sin: Calculates the value of a sinusoidal voltage source at a given time.
- pulse: Calculates the value of a pulse voltage source at a given time.
- dc: Returns a constant DC voltage value.
"""

__all__ = [
            "PulseVoltageSource",
            "SinusoidalVoltageSource",
            "VoltageSourceControlByVoltage",
            "CurrentSourceControlByVoltage",
            "CurrentSourceControlByVoltage",
            "VoltageSourceControlByCurrent",
            "sin",
            "pulse",
            "dc"
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
        attenuation      : float=0,
        delay            : float=0
        ) -> float:
    """
    Calculates the value of a sinusoidal voltage source at time t.
    """
    if (t < delay) or (t>(delay + (1/frequency)*number_of_cycles)):
        V = dc + amplitude * np.sin( (np.pi * angle)/180 )
    else:
        V = (dc + amplitude*np.exp( -1 * attenuation * (t-delay) )) * np.sin( 2*np.pi*frequency*(t-delay) + (np.pi*angle)/180 )
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



#
# Signal sources
#


class SinusoidalVoltageSource(Source):

    def __init__(self,
                     nodeIn           : int,
                     nodeOut          : int,
                     amplitude        : float,
                     frequency        : float,
                     number_of_cycles : int,
                     dc               : float=0,
                     delay            : float=0,
                     angle            : float=0,
                     attenuation      : float=0,
                     name             : str=""
                    ):
                """
                Initializes an instance of the IndependentSource class.

                Parameters:
                nodeIn (int): The input node number.
                nodeOut (int): The output node number.
                amplitude (float): The amplitude of the source.
                frequency (float): The frequency of the source.
                number_of_cycles (int): The number of cycles for the source.
                dc (float, optional): The DC offset. Defaults to 0.
                delay (float, optional): The delay before the source starts. Defaults to 0.
                angle (float, optional): The phase angle of the source. Defaults to 0.
                attenuation (float, optional): The attenuation parameter for the source. Defaults to 0.
                name (str, optional): The name of the source. Defaults to an empty string.
                """

                IndependentSource.__init__(self, name, nodeIn, nodeOut)
                self.amplitude = amplitude
                self.frequency = frequency
                self.number_of_cycles = number_of_cycles
                self.dc        = dc
                self.angle     = angle
                self.attenuation     = attenuation
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
                        self.attenuation, 
                        self.delay)

        # Update the matrix A and vector b for the voltage source
        A[self.nodeIn, jx]  +=  1
        A[self.nodeOut, jx] += -1
        A[jx, self.nodeIn]  += -1
        A[jx, self.nodeOut] +=  1
        b[jx] += V
        return current_branch





    @classmethod
    def from_nl( cls, params : Tuple[str, str, int, int, str, float, float, float, float, float, float, int] ) -> SinusoidalVoltageSource:
        
        # Vsin: I/V, name, nodeIn, nodeOut, 'SIN', DC, AMPLITUDE, FREQ, DELAY, ATTENUATION (alpha), ANGLE, NUMBER_OF_CYCLES
        if params[0] != 'I' or params[1] != 'V':
            raise InvalidElement(f"Invalid parameters for SinusoidalVoltageSource: expected 'V' or 'I' ({params[0]}) as first element.")
        
        if params[4] != "SIN" and len(params) != 12:
            raise InvalidElement(f"Invalid parameters for SinusoidalVoltageSource: expected 'SIN' ({params[4]}) as third element and 12 {len(params)} parameters in total.")

        return SinusoidalVoltageSource (nodeIn=params[2], 
                                        nodeOut=params[3], 
                                        amplitude=params[6], 
                                        frequency=params[7], 
                                        number_of_cycles=params[11],
                                        dc=params[5],
                                        delay=params[8],
                                        angle=params[10],
                                        attenuation=params[9],
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
             attenuation       : float=0,
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
        attenuation (float, optional): The damping factor for the source signal. Default is 0.
        name (str, optional): The name of the source. Default is an empty string.

        """
        
        Source.__init__(self, nodeIn, nodeOut, name=name)
        self.amplitude = amplitude
        self.frequency = frequency
        self.number_of_cycles = number_of_cycles
        self.dc        = dc
        self.angle     = angle
        self.attenuation     = attenuation
        self.delay     = delay


    def backward(self, A, b, t : float=0, deltaT : float=0, current_branch : int=0):

        V = self.pulse(t,...)
        A[self.nodeIn,self.jx] +=  1
        A[self.nodeOut,self.jx] += -1
        A[self.jx, self.nodeIn] += -1
        A[self.jx, self.nodeOut] +=  1
        b[self.jx] += -V
        return current_branch


    @classmethod
    def from_nl( cls, params : Tuple[str, str, int, int, float, float, int, float, float, float]] ) -> PulseVoltageSource:
        # PulseVoltageSource: 'I/V', name, nodeIn, nodeOut, 'PULSE', AMPLITUDE_1, AMPLITUDE_2, DELAY, RISE_TIME, FALL_TIME, TIME_ON, PERIOUD, NUMBER_OF_CYCLES
        if params[0] != 'I' or params[1] != 'V':
            raise InvalidElement(f"Invalid parameters for PulseVoltageSource: expected 'I/V' ({params[0]}) as first element.")
        if params[4] != "PULSE" and len(params) != 13:
            raise InvalidElement(f"Invalid parameters for PulseVoltageSource: expected 'PULSE' ({params[4]}) as third element and 13 ({len(params)}) parameters in total.")
        return PulseVoltageSource( nodeIn=params[2],
                                   nodeOut=params[3],
                                   amplitude_1=params[5],
                                   amplitude_2=params[6],
                                   delay=params[7],
                                   rise_time=params[8],
                                   fall_time=params[9],
                                   time_on=params[10],
                                   T=params[11],
                                   number_of_cycles=params[12])



#
# Voltage and current source gains
#


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
    def from_nl( cls, params : Tuple[str, str, int, int, int, int, float] ) -> VoltageSourceControlByVoltage:
        # VoltageSourceControlByVoltage: 'E', name, noIn, noOut, control_noIn, control_noOut, Av
        if params[0] != 'E' or len(params) != 7:
            raise InvalidElement(f"Invalid parameters for VoltageSourceControlByVoltage: expected 'E'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
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


    @classmethod
    def from_nl( cls, params : Tuple[str, str, int, int, int, int, float] ) -> CurrentSourceControlByVoltage:
        # CurrentSourceControlByVoltage: 'F', name, noIn, noOut, control_noIn, control_noOut, Ai
        if params[0] != 'F' or len(params) != 7:
            raise InvalidElement(f"Invalid parameters for CurrentSourceControlByVoltage: expected 'F'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return CurrentSourceControlByVoltage( nodeIn=params[2], 
                                              nodeOut=params[3], 
                                              controlNodeIn=params[4], 
                                              controlNodeOut=params[5], 
                                              Ai=params[6],
                                              name=params[1])


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


    @classmethod
    def from_nl( cls, params : Tuple[str, str, int, int, int, int, float] ) -> CurrentSourceControlByVoltage:
        # CurrentSourceControlByVoltage: 'G', name, noIn, noOut, control_noIn, control_noOut, Gm
        if params[0] != 'G' or len(params) != 7:
            raise InvalidElement(f"Invalid parameters for CurrentSourceControlByVoltage: expected 'G'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return CurrentSourceControlByVoltage( nodeIn=params[2], 
                                              nodeOut=params[3], 
                                              controlNodeIn=params[4], 
                                              controlNodeOut=params[5], 
                                              Gm=params[6],
                                              name=params[1])


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


    @classmethod
    def from_nl( cls, params : Tuple[str, str, int, int, int, int, float] ) -> VoltageSourceControlByCurrent:
        # VoltageSourceControlByCurrent: 'H', name, noIn, noOut, control_noIn, control_noOut, Rm
        if params[0] != 'H' or len(params) != 7:
            raise InvalidElement(f"Invalid parameters for VoltageSourceControlByCurrent: expected 'H'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return VoltageSourceControlByCurrent( nodeIn=params[2], 
                                              nodeOut=params[3], 
                                              controlNodeIn=params[4], 
                                              controlNodeOut=params[5], 
                                              Rm=params[6],
                                              name=params[1])