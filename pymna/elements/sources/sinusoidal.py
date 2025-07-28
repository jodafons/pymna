__all__ = [
    "SinusoidalVoltageSource",
    "SinusoidalCurrentSource",
]

import numpy as np
from pymna.elements import Element
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

class SinusoidalVoltageSource(Element):

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
        Element.__init__(self, name=name)
        self.nodeIn = nodeIn
        self.nodeOut = nodeOut
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
