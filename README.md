
# Pymna


Pymna is a Python package designed for circuit analysis in both time and frequency domains. It provides a user-friendly interface for simulating and analyzing electrical circuits, making it an essential tool for engineers and researchers. With Pymna, users can easily create complex circuit configurations, apply various voltage sources, and observe the resulting behavior over time. The package supports a wide range of components, including resistors, capacitors, and nonlinear elements, enabling detailed exploration of circuit dynamics and stability. Whether for educational purposes or advanced research, Pymna simplifies the process of circuit analysis and enhances understanding of electrical systems.

## Installation

You can install Pymna using pip:

```
pip install pymna
```

## Usage

The Chua circuit is a well-known example of a chaotic circuit that exhibits complex dynamical behavior. It consists of two resistors, a capacitor, and a nonlinear resistor known as the Chua diode. The circuit is driven by a sinusoidal voltage source, which introduces periodic behavior. 

In this example, the resistors R1 and R2 are connected in series with the capacitor C1, while the Chua diode provides the nonlinear characteristics necessary for chaos. The sinusoidal voltage source V1 applies an alternating voltage to the circuit, influencing the overall dynamics. 

This setup allows for the exploration of chaotic behavior and can be used in various applications, including chaos theory studies and electronic circuit demonstrations.

This example sets up a basic Chua circuit with resistors, a capacitor, and a nonlinear resistor (Chua diode) along with a sinusoidal voltage source.

```python
# Create a circuit
circuit = Circuit(name="Chua Circuit")
# Add components to the circuit
circuit.R('node1', 'node2', 1e3, name='R1')  # Resistor R1
circuit.R('node2', 'node3', 1e3, name='R2')  # Resistor R2
circuit.C('node3', 'gnd', 1e-6, name='C1')   # Capacitor C1
circuit.NoLinearResistor('node1', 'node2', 
                         nolinear_voltage_1=0.5, 
                         nolinear_current_1=0.1, 
                         nolinear_voltage_2=-0.5, 
                         nolinear_current_2=-0.1, 
                         nolinear_voltage_3=0.0, 
                         nolinear_current_3=0.0, 
                         nolinear_voltage_4=0.0, 
                         nolinear_current_4=0.0, 
                         name='Chua Diode')
circuit.SinusoidalVoltageSource('node1', 'gnd', amplitude=5, frequency=1000, number_of_cycles=10, name='V1')
```

