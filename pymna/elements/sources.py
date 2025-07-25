"""
This module defines various source elements used in electrical circuit simulations.
It includes classes for different types of voltage and current sources, such as
sinusoidal and pulse sources. Each source can be characterized by its parameters
like amplitude, frequency, and delay. The module provides functions to calculate
the voltage or current at a given time based on these parameters.

Classes:
    - Source: Base class for all sources.
    - SinusoidalVoltageSource: Represents a sinusoidal voltage source.
    - SinusoidalCurrentSource: Represents a sinusoidal current source.
    
Functions:
    - sin: Calculates the value of a sinusoidal voltage source at a given time.
    - pulse: Calculates the value of a pulse voltage source at a given time.
    - dc: Returns a constant DC voltage value.
"""
"""

"""

__all__ = [
    "VoltageSource",
    "CurrentSource",
    "SinusoidalVoltageSource",
    "SinusoidalCurrentSource",
    "PulseVoltageSource",
    "PulseCurrentSource",
    "VoltageSourceControlByVoltage",
    "CurrentSourceControlByCurrent",
    "CurrentSourceControlByVoltage",
    "VoltageSourceControlByCurrent",

]

import numpy as np

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

    Parameters:
        t (float): The time at which to calculate the voltage.
        amplitude (float): The amplitude of the sinusoidal source.
        frequency (float): The frequency of the sinusoidal source.
        number_of_cycles (int): The number of cycles for the source.
        dc (float, optional): The DC offset. Defaults to 0.
        angle (float, optional): The phase angle of the source. Defaults to 0.
        attenuation (float, optional): The attenuation parameter for the source. Defaults to 0.
        delay (float, optional): The delay before the source starts. Defaults to 0.

    Returns:
        float: The calculated voltage at time t.
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

def dc(dc    : float 
       ) -> float:
    """
    Returns a constant DC voltage value.

    Parameters:
        dc (float): The DC voltage value to return.

    Returns:
        float: The constant DC voltage value.
    """
    return dc

class Source:
    
    def __init__(self,
                 name    : str,
                 nodeIn  : int,
                 nodeOut : int,
                 ):
        """
        Initializes a Source object.
        This class represents a source in a circuit, which can be used to
        provide voltage or current to a circuit.

        Parameters:
            name (str): The name of the source.
            nodeIn (int): The input node number.
            nodeOut (int): The output node number.
        """
        self.nodeIn   = nodeIn
        self.nodeOut  = nodeOut
        self.name     = name

class VoltageSource(Source):
    def __init__(self, 
                 nodeIn  : int,
                 nodeOut : int,
                 V       : float=0,
                 name    : str=""
            ):
        """
        Initializes a DCVoltageSource object with the given parameters.
        This class represents a DC voltage source in a circuit simulation.

        Parameters:
            nodeIn (int): The input node of the source.
            nodeOut (int): The output node of the source.
            dc (float, optional): The DC voltage value. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.
        """
        Source.__init__(self, name, nodeIn, nodeOut)
        self.V = V

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:

        A[self.nodeIn,self.jx]   +=  1
        A[self.nodeOut,self.jx]  += -1
        A[self.jx, self.nodeIn]  += -1
        A[self.jx, self.nodeOut] +=  1
        b[self.jx] += -self.V
        return current_branch

class CurrentSource(Source):
    def __init__(self, 
                 nodeIn  : int,
                 nodeOut : int,
                 I       : float=0,
                 name    : str=""
            ):
        """
        Initializes a DCCurrentSource object with the given parameters.
        This class represents a DC current source in a circuit simulation.

        Parameters:
            nodeIn (int): The input node of the source.
            nodeOut (int): The output node of the source.
            dc (float, optional): The DC current value. Defaults to 0.
            name (str, optional): The name of the source. Defaults to an empty string.
        """
        Source.__init__(self, name, nodeIn, nodeOut)
        self.I = I

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
        I = self.I
        b[self.nodeIn]   += -I
        b[self.nodeOut]  +=  I
        return current_branch

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
        Initializes an instance of the SinusoidalVoltageSource class.

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
        Source.__init__(self, name, nodeIn, nodeOut)
        self.amplitude   = amplitude
        self.frequency   = frequency
        self.number_of_cycles = number_of_cycles
        self.dc          = dc
        self.angle       = angle
        self.attenuation = attenuation
        self.delay       = delay

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
                 
        V = self.sin(t, self.amplitude, 
                        self.frequency, 
                        self.number_of_cycles, 
                        self.dc, 
                        self.angle, 
                        self.attenuation, 
                        self.delay)
        Vs = VoltageSource(self.nodeIn, self.nodeOut, V)
        return Vs.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

    @classmethod
    def from_nl(cls, params: Tuple[str, int, int, str, float, float, float, float, float, float, int]):
        """
        Creates a SinusoidalVoltageSource instance from a parameter tuple.

        Parameters:
            cls: The class itself.
            params (Tuple): A tuple containing parameters for the source.

        Returns:
            SinusoidalVoltageSource: An instance of the SinusoidalVoltageSource class.
        """
        # Vsin: I/Vname, nodeIn, nodeOut, 'SIN', DC, AMPLITUDE, FREQ, DELAY, ATTENUATION (alpha), ANGLE, NUMBER_OF_CYCLES
        if params[0][0] != 'I' or params[0][0] != 'V':
            raise InvalidElement(f"Invalid parameters for SinusoidalVoltageSource: expected 'V' or 'I' ({params[0]}) as first element.")
        
        if params[3] != "SIN" and len(params) != 11:
            raise InvalidElement(f"Invalid parameters for SinusoidalVoltageSource: expected 'SIN' ({params[3]}) as third element and 11 {len(params)} parameters in total.")

        return SinusoidalVoltageSource( nodeIn=int(params[1]), 
                                        nodeOut=int(params[2]), 
                                        amplitude=float(params[5]), 
                                        frequency=float(params[6]), 
                                        number_of_cycles=int(params[10]),
                                        dc=float(params[4]),
                                        delay=float(params[7]),
                                        angle=float(params[9]),
                                        attenuation=float(params[8]),
                                        name=params[0])

class SinusoidalCurrentSource(SinusoidalVoltageSource):
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
        Initializes an instance of the SinusoidalCurrentSource class.

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
        SinusoidalVoltageSource.__init__(self,
                                            nodeIn=nodeIn,
                                            nodeOut=nodeOut,
                                            amplitude=amplitude,
                                            frequency=frequency,
                                            number_of_cycles=number_of_cycles,
                                            dc=dc,
                                            delay=delay,
                                            angle=angle,
                                            attenuation=attenuation,
                                            name=name)

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
                 
        I = sin(t, 
                self.amplitude, 
                self.frequency, 
                self.number_of_cycles, 
                self.dc, 
                self.angle, 
                self.attenuation, 
                self.delay)
        Is = CurrentSource(self.nodeIn, self.nodeOut, I)
        return Is.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

class PulseVoltageSource(Source):

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
        Source.__init__(self, name, nodeIn, nodeOut)
        self.amplitude   = amplitude
        self.frequency   = frequency
        self.number_of_cycles = number_of_cycles
        self.dc          = dc
        self.angle       = angle
        self.attenuation = attenuation
        self.delay       = delay

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:

        V = self.pulse(t,
                        self.amplitude_1,
                        self.amplitude_2,
                        self.T,
                        self.rise_time,
                        self.fall_time,
                        self.time_on,
                        self.delay)

        Vs = VoltageSource(self.nodeIn, self.nodeOut, V)
        return Vs.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

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
        Initializes a PulseCurrentSource object with the given parameters.
        This class represents a pulse current source in a circuit simulation.
        """
        PulseVoltageSource.__init__(self, nodeIn, nodeOut, amplitude_1, amplitude_2, T, number_of_cycles, delay, rise_time, fall_time, time_on, angle, attenuation, name)

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:
                 
        I = self.pulse(t,
                        self.amplitude_1,
                        self.amplitude_2,
                        self.T,
                        self.rise_time,
                        self.fall_time,
                        self.time_on,
                        self.delay)
        Is = CurrentSource(self.nodeIn, self.nodeOut, I)
        return Is.backward(A, b, x, x_newton_raphson, t, dt, current_branch)

#
# Voltage and current source gains
#

class VoltageSourceControlByVoltage(Source):

    # This class represents a voltage source controlled by another voltage source.
    # The letter is 'E'.
    def __init__(self, 
                 nodeIn          : int,
                 nodeOut         : int,
                 controlNodeIn   : int,
                 controlNodeOut  : int,
                 Av              : float,
                 name            : str=""
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
        
        Source.__init__(self, name, nodeIn, nodeOut)
        self.Av = Av
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

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
        A[self.nodeIn , jx]        +=  1
        A[self.nodeOut , jx]       += -1
        A[jx, self.nodeIn]         += -1
        A[jx, self.nodeOut]        +=  1
        A[jx, self.controlNodeIn]  += self.Av
        A[jx, self.controlNodeOut] += -self.Av 
        return current_branch

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # VoltageSourceControlByVoltage: 'E'name, noIn, noOut, control_noIn, control_noOut, Av
        if params[0][0] != 'E' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for VoltageSourceControlByVoltage: expected 'E'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return VoltageSourceControlByVoltage( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Av=float(params[5]),
                                              name=params[0])
 
class CurrentSourceControlByCurrent:
   
   # This class represents a current source controlled by a voltage source.
   # The letter if 'F'
    def __init__(self, 
             nodeIn         : int,
             nodeOut        : int,
             controlNodeIn  : int,
             controlNodeOut : int,
             Ai             : float,
             name           : str=""
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
        Source.__init__(self, name, nodeIn, nodeOut)
        self.Ai = Ai
        self.controlNodeIn  = controlNodeIn
        self.controlNodeOut = controlNodeOut

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
        A[self.controlNodeIn , jx]   +=  1
        A[self.controlNodeOut, jx]   += -1
        A[jx, self.controlNodeIn]    += -1
        A[jx, self.controlNodeOut]   +=  1
        A[self.nodeIn , jx]          +=  self.Ai
        A[self.nodeOut , jx]         += -self.Ai
        return current_branch

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # CurrentSourceControlByVoltage: 'F'name, noIn, noOut, control_noIn, control_noOut, Ai
        if params[0][0] != 'F' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for CurrentSourceControlByCurrent expected 'F'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return CurrentSourceControlByCurrent( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Ai=float(params[5]),
                                              name=params[0])

# Trancondutance
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
        Source.__init__(self, name, nodeIn, nodeOut)
        self.Gm = Gm
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

    def backward(self, 
                 A                : np.array, 
                 b                : np.array, 
                 x                : np.array,
                 x_newton_raphson : np.array,
                 t                : float,
                 dt               : float,
                 current_branch   : int, 
                 ) -> int:

        A[self.nodeIn, self.controlNodeIn   ] +=  self.Gm
        A[self.nodeIn, self.controlNodeOut  ] += -self.Gm
        A[self.nodeOut, self.controlNodeIn  ] += -self.Gm
        A[self.nodeOut, self.controlNodeOut ] +=  self.Gm
        return current_branch

    @classmethod
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # CurrentSourceControlByVoltage: 'G'name, noIn, noOut, control_noIn, control_noOut, Gm
        if params[0] != 'G' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for CurrentSourceControlByVoltage: expected 'G'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return CurrentSourceControlByVoltage( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Gm=float(params[5]),
                                              name=params[0])

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
        
        Source.__init__(self, name, nodeIn, nodeOut)
        self.Rm = Rm
        self.controlNodeIn = controlNodeIn
        self.controlNodeOut = controlNodeOut

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
    def from_nl( cls, params : Tuple[str, int, int, int, int, float] ):
        # VoltageSourceControlByCurrent: 'H'name, noIn, noOut, control_noIn, control_noOut, Rm
        if params[0][0] != 'H' or len(params) != 6:
            raise InvalidElement(f"Invalid parameters for VoltageSourceControlByCurrent: expected 'H'({params[0]}) as first element and 7 ({len(params)})parameters in total.")
        return VoltageSourceControlByCurrent( nodeIn=int(params[1]), 
                                              nodeOut=int(params[2]), 
                                              controlNodeIn=int(params[3]), 
                                              controlNodeOut=int(params[4]), 
                                              Rm=float(params[5]),
                                              name=params[0])