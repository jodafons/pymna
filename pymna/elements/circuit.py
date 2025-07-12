



class Circuit:
    def __init__(self, name : str=""):
        self.name = name
        self.elements = []
        self.gnd = 0

    def __add__(self, element):
        self.elements.append(element)
        return self

    

    def C(self,
          a : int,
          b : int,
          capacitance : float,
          name : str="",
          initial_condition : float=0
          ):
        
        capacitor = Capacitor(a,b,capacitance, initial_condition=initial_condition, name=name)
        self.elements.append(capacitor)
        return capacitor
    
    def R(self,
          a : int,
          b : int,
          resistence : float,
          name : str=""):

        resistor = Resistor(a,b,resistence,name=name)
        self.__add__(resistor)
        return resistor



if __name__ == "__main__":

    circuit = Circuit(name="RC")
    circuit.SinusoidalVoltageSource(circuit.new_node(), circuit.gnd,  amplitude=1*V, freq=60*Hz, name="input")
    circuit.R( 1, 2, 100, name="R1")
    circuit.C( 2, circuit.gnd, 50*uF, name="C1" )
    simulator = TimeSimulator( start=0, end=5*minutes )
    simulator.run( circuit )

