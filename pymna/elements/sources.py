

__all__ = [
            "PulseVoltageSource",
            "SinusoidalVoltageSource",
        ]

from pymna import enumerator as enum
from pymna.exceptions import InvalidElement
from typing import Tuple
from abc import ABC



class IndependentSource:

    def __init__(self,
                 name     : str,
                 positive : int,
                 negative : int,
                 ):
        self.positive = positive
        self.negative = negative
        self.name     = name


    def sin(self,
            t                : float,
            amplitude        : float,
            frequency        : float,
            number_of_cycles : int,
            dc               : float=0,
            angle            : float=0,
            alpha            : float=0,
            delay            : float=0
            ) -> float:
        if (t < delay) or (delay + (1/frequency)*number_of_cycles)
            V = dc + amplitude * np.sin( (np.pi * angle)/180 )
        else:
            V = (dc + amplitude*np.exp( -1 * alpha * (t-delay) )) * np.sin( 2*np.pi*frequency*(t-delay) + (np.pi*angle)/180 )
        return V


    def pulse(self,
              t               : float,
              step            : float,
              amplitude_1     : float,
              amplitude_2     : float,
              T               : float,
              rise_time       : float=0,
              fall_time       : float=0,
              time_on         : float=0,
              delay           : float=0):

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


    def dc(self,
           t     : float,
           dc    : float 
           ):
        return dc




class SinusoidalVoltageSource(IndependentSource):

    def __init__(self,
                 positive  : int,
                 negative  : int,
                 amplitude : float,
                 frequency : float,
                 number_of_cycles : int,
                 dc        : float=0,
                 delay     : float=0,
                 angle     : float=0,
                 alpha     : float=0,
                 name      : str=""
                ):

        IndependentSource.__init__(self, name, positive, negative)
        self.amplitude = amplitude
        self.frequency = frequency
        self.number_of_cycles = number_of_cycles
        self.dc        = dc
        self.angle     = angle
        self.alpha     = alpha
        self.delay     = delay

    def backward( self, A, b , t : int, deltaT : float, current_branch : int) -> int:

        V = self.sin(t, self,amplitude, self,frequency, self.number_of_cycles, self.dc, self.angle, self.alpha, self.delay)
        current_branch += 1
        jx = current_branch
        A[self.positive, jx] +=  1
        A[self.negative, jx] += -1
        A[jx, self.positive] += -1
        A[jx, self.negative] +=  1
        b[jx] += V
        return current_branch


class PulseVoltageSource(IndependentSource):

    def __init__(self,
                 positive    : int,
                 negative    : int,
                 amplitude_1 : float,
                 amplitude_2 : float,
                 T           : float,
                 number_of_cycles : int=1,
                 delay       : float=0,
                 rise_time   : float=0,
                 fall_time   : float=0,
                 time_on     : float=0
                 angle       : float=0,
                 alpha       : float=0,
                 name        : str=""
                ):

        Source.__init__(self, positive, negative, name=name)
        simulator      = get_simulator_service()
        self.jx        = simulator.create_current()
        self.amplitude = amplitude
        self.frequency = frequency
        self.number_of_cycles = number_of_cycles
        self.dc        = dc
        self.angle     = angle
        self.alpha     = alpha
        self.delay     = delay


    def backward( self, A, b , t : int , ):
        V = self.pulse(t,...)
        A[self.positive,self.jx] +=  1
        A[self.negative,self.jx] += -1
        A[self.jx, self.positive] += -1
        A[self.jx, self.negative] +=  1
        b[self.jx] += -V



