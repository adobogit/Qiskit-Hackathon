# -*- coding: utf-8 -*-
"""Copy of QiskitScholar 2.0

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1U4LoyTgf_HJkLZlQlY93FCBBjC9Acgaq
"""

!pip install qiskit
!pip install qiskit-aer
!pip install matplotlib
!pip install pylatexenc

from qiskit import QuantumCircuit, transpile
#from qiskit_aer import Aer
from qiskit.circuit.library import GroverOperator
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import MCXGate
from collections import Counter

# Import section
from qiskit_aer import AerSimulator

# Number of qubits required to represent 100 papers (7 qubits for 128 states)
n = 7  # 2^7 = 128 states, enough to cover 100 papers

# Create the quantum circuit
qc = QuantumCircuit(n)

# Step 1: Initialize the qubits in a superposition state
qc.h(range(n))  # Apply Hadamard gates to all qubits for superposition

# Step 2: Define the Oracle (Mark multiple relevant papers)
# Let's assume the relevant papers are represented by binary indices:
# |0110011⟩ (binary 51), |0101010⟩ (binary 42), |0011100⟩ (binary 28),
# |1100110⟩ (binary 102), and |1001011⟩ (binary 75)

# Oracle circuit to mark multiple relevant papers
oracle = QuantumCircuit(n)

# Mark each state by flipping the bits that are 0 to convert each to |0000000⟩
states_to_mark = [51, 42, 28, 102, 75]
for state in states_to_mark:
    binary_state = format(state, f'0{n}b')
    # Flip qubits to match each binary pattern
    for qubit, bit in enumerate(binary_state):
        if bit == '0':
            oracle.x(qubit)
    # Apply controlled-Z to mark this state
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)
    oracle.h(n - 1)
    # Flip qubits back to the original state
    for qubit, bit in enumerate(binary_state):
        if bit == '0':
            oracle.x(qubit)

# Combine oracle with the main circuit
qc.append(oracle, range(n))

# Step 3: Diffusion Operator (Grover's Diffusion Operator)
# The diffusion operator amplifies the probability of the marked states
diffusion = QuantumCircuit(n)
diffusion.h(range(n))    # Apply Hadamard to all qubits
diffusion.x(range(n))    # Apply X gates to all qubits
diffusion.h(n - 1)       # Apply Hadamard on the last qubit
diffusion.mcx(list(range(n - 1)), n - 1)  # Multi-controlled Z
diffusion.h(n - 1)       # Uncompute the Hadamard on the last qubit
diffusion.x(range(n))    # Apply X gates to all qubits
diffusion.h(range(n))    # Apply Hadamard to all qubits

# Add the diffusion operator to the main circuit
# Repeat Oracle and Diffusion approximately sqrt(128) times
num_iterations = 11  # √128 ≈ 11 for optimal probability amplification
for _ in range(num_iterations):
    qc.append(oracle, range(n))
    qc.append(diffusion, range(n))

def Grover(n, indices_of_marked_elements):
    # Create the main quantum circuit for Grover's algorithm
    grover_circuit = QuantumCircuit(n)

    # Step 1: Initialize the qubits in superposition
    grover_circuit.h(range(n))  # Apply Hadamard gates to all qubits

    # Step 2: Define the Oracle to mark the relevant states
    oracle = QuantumCircuit(n, name="Oracle")

    for state in indices_of_marked_elements:
        binary_state = format(state, f'0{n}b')
        # Flip qubits to match each binary pattern
        for qubit, bit in enumerate(binary_state):
            if bit == '0':
                oracle.x(qubit)
        # Apply controlled-Z to mark this state
        oracle.h(n - 1)
        oracle.mcx(list(range(n - 1)), n - 1)
        oracle.h(n - 1)
        # Flip qubits back to the original state
        for qubit, bit in enumerate(binary_state):
            if bit == '0':
                oracle.x(qubit)

    # Add the oracle as a gate to the main circuit
    grover_circuit.append(oracle.to_gate(), range(n))

    # Step 3: Define the Diffusion Operator (Grover's Diffusion Operator)
    diffusion = QuantumCircuit(n, name="Diffusion")

    diffusion.h(range(n))    # Apply Hadamard to all qubits
    diffusion.x(range(n))    # Apply X gates to all qubits
    diffusion.h(n - 1)       # Apply Hadamard on the last qubit
    diffusion.mcx(list(range(n - 1)), n - 1)  # Multi-controlled Z
    diffusion.h(n - 1)       # Uncompute the Hadamard on the last qubit
    diffusion.x(range(n))    # Apply X gates to all qubits
    diffusion.h(range(n))    # Apply Hadamard to all qubits

    # Add Grover iterations (Oracle + Diffusion)
    num_iterations = int(round(3.14 / 4 * (2 ** (n / 2))))  # Approximate sqrt(N) for Grover's iterations
    for _ in range(num_iterations):
        grover_circuit.append(oracle.to_gate(), range(n))
        grover_circuit.append(diffusion.to_gate(), range(n))

    # Step 4: Add measurement
    grover_circuit.measure_all()

    return grover_circuit

# Example usage
n = 6  # Number of qubits
indices_of_marked_elements = [1, 42]  # Indices of marked elements
mycircuit = Grover(n, indices_of_marked_elements)

# Draw the circuit
mycircuit.draw('mpl')

# Step 5: Measurement
qc.measure_all()

# Visualize the circuit
qc.draw('mpl')

# For execution
simulator = AerSimulator()
compiled_circuit = transpile(qc, simulator)
sim_result = simulator.run(compiled_circuit).result()
counts = sim_result.get_counts()

# Display the results
print("Top 5 most relevant papers:")
top_5 = Counter(counts).most_common(5)
for i, (state, count) in enumerate(top_5, start=1):
    decimal_state = int(state.replace(" ", ""), 2)
    print(f"Rank {i}: Paper index {decimal_state} with {count} occurrences")

# Show the result as a histogram
plot_histogram(counts)